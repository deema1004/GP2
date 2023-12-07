from .models import ChatRoom, ChatMessage, ChatMessageFile
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from json import JSONDecodeError

User = get_user_model()
channel_layer = get_channel_layer()


@sync_to_async
def async_get_chat_room(id):
    obj = ChatRoom.objects.get(id=id)
    return obj


def get_chat_room(id):
    obj = ChatRoom.objects.get(id=id)
    return obj

def get_user(user_id):
    obj = User.objects.get(id=user_id)
    return obj


@sync_to_async
def make_a_message_seen(message_id):
    message_obj = ChatMessage.objects.get(id=message_id)
    message_obj.seen = True
    message_obj.save()

    return [message_obj.room, message_obj]


@sync_to_async
def make_all_messages_of_user_seen(room_id, user):
    room = get_chat_room(room_id)
    messages = room.messages.filter(seen=False)
    other_user = room.user1
    if user == other_user:
        other_user = room.user2
    
    messages = messages.filter(user=other_user)
    print("mess --> ", messages)
    exists = False
    if messages.exists():
        exists = True
    messages.update(seen=True)
    return [room, exists]


@sync_to_async
def save_chat_message(data_dict):
    room = data_dict.get("room")
    if room == "new_room":
        user2_id = data_dict.get("user_id", None)
        if not user2_id:
            raise ValueError("provide 'user_id' to send message")
        
        user2 = get_user(user2_id)
        print("User --> ", user2.id)
        print("\n\n")

        chat_room = ChatRoom.objects.get_or_create_room(data_dict.get("user"), user2)
        chat_room.save()
    else:
        chat_room = get_chat_room(room)

    message = data_dict.get("message", None)
    if message == "":
        message = None
    files = data_dict.get("files", None)
    user = data_dict.get("user")
    files = data_dict.get("files", None)

    chat_msg = ChatMessage.objects.create(room=chat_room, message=message, user=user)

    if files is not None:
        files = list(files)
        print("FILES --> ", files)
        for file_ in files:
            try:
                file_ = dict(file_)
                print("EACH FILE --> ", file_)
                file_url = file_.get("file")
                if file_url is not None:
                    print("file URL ", file_url)
                    chat_msg.files.create(file=file_url)
                    print("CREATED")
            except JSONDecodeError as e:
                print("ERROR --<> ", e)

    return chat_msg

def send_by_websocket(chat_room, data):
    async_to_sync(channel_layer.group_send)(
            chat_room, 
            {
                "type": "send.message",
                "text": data,
            }
        )


def get_all_userids_in_user_room(user):
    userid_list = []
    qs = ChatRoom.objects.filter(user1=user)
    userid_list.extend(list(qs.values_list("user2", flat=True)))

    qs = ChatRoom.objects.filter(user2=user)
    userid_list.extend(list(qs.values_list("user1", flat=True)))

    return userid_list


def get_user_unseen_msgs_count(user, room=None):
    if room:
        rooms = ChatRoom.objects.filter(room=room)
    else:
        rooms = ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))
    
    counter = ChatMessage.objects.filter(room__in=rooms, seen=False).count()
    return counter
