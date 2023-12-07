import json
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import ChatRoom, ChatMessage, UserOnlineStatus
from .serializers import ChatRoomSerializer, ChatMessageSerializer, UserSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .utils import send_by_websocket, get_all_userids_in_user_room
from django.core.mail import send_mail
from django.conf import settings

channel_layer = get_channel_layer()


@receiver(sender=ChatMessage, signal=post_save)
def send_notification_to_user(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        room = instance.room
    
        if user == room.user1:
            to_user = room.user2
        else:
            to_user = room.user1
        
        rooms = ChatRoom.objects.filter(Q(user1=to_user) | Q(user2=to_user))
        counter = ChatMessage.objects.filter(~Q(user=to_user), room__in=rooms, seen=False).count()
        chat_room = f"notification_room_{to_user.id}"
        data = {
            "command": "incoming_message",
            "count": counter
        }
        async_to_sync(channel_layer.group_send)(
                chat_room, 
                {
                    "type": "send.notification",
                    "text": data,
                }
            )


@receiver(sender=ChatMessage, signal=post_save)
def async_send_to_users(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        room.save()


@receiver(sender=UserOnlineStatus, signal=post_save)
def send_online_or_offline_response_to_other_users(sender, instance, created, **kwargs):
    user = instance.user
    chat_rooms = ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))

    for ch_room in chat_rooms:
        if ch_room.user1 == user:
            other_user = ch_room.user2
        else:
            other_user = ch_room.user1
        data = {
            "user_online_status": instance.online,
            "user": UserSerializer(user).data,
            "room": ChatRoomSerializer(ch_room).data,
            "related_ad": AdSerializer(ch_room.ad).data,
        }
        chat_room = f"room_{other_user.id}"
        send_by_websocket(chat_room, data)


@receiver(signal=post_save, sender=ChatMessage)
def send_email_if_user_not_online(sender, instance, created, **kwargs):
    if not created:
        return None
    
    user_online_stat = UserOnlineStatus.objects.filter().order_by("-created").first()
    if user_online_stat.online:
        return False
    
    to_user = instance.room.user1
    if instance.user == to_user:
        to_user = instance.room.user2

    send_mail(
        subject="Incoming Message",
        message=f"Recieved message from {instance.user}",
        from_email=settings.HOST_USER_EMAIL,
        recipient_list=[to_user.email, ]
    )
    print("Email Sent")
    return True

