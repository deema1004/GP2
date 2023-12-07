import uuid
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def uuid_without_dash():
    return uuid.uuid4().hex


class ChatRoomManager(models.Manager):

    def get_or_create_room(self, user1, user2):
        if type(user1) == type(""):
            user1 = User.objects.get(id=user1)

        if type(user2) == type(""):
            user2 = User.objects.get(id=user2)

        if user1 == user2:
            raise ValueError("Users cannot create room between itself.")

        qs = self.filter(Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1))
        if not qs.exists():
            obj = self.create(user1=user1, user2=user2)
            return obj

        return qs.get()

    def get_user_rooms(self, user: User):
        assert isinstance(user, User)
        qs = self.filter(Q(user1=user) | Q(user2=user))
        return qs


class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          editable=False, default=uuid_without_dash)

    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user1_rooms")
    
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user2_rooms")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = ChatRoomManager()

    class Meta:
        ordering = ["-modified", ]

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        user1 = self.user1
        user2 = self.user2

        if user1 == user2:
            raise ValueError("User cannot create between themselves")

        return super().save(*args, **kwargs)

# ChatMessage.objects.filter(room__ad=ad_id, seen=False).count()


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          editable=False, default=uuid_without_dash)
    room = models.ForeignKey(
        ChatRoom, on_delete=models.SET_NULL, null=True, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.TextField(null=True, blank=True)
    seen = models.BooleanField(default=False)
    # image = models.CharField(max_length=5000, null=True, blank=True)
    # files = models.FileField(upload_to="chat/files")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created", ]

    def __str__(self):
        return f"msg-{self.id}"

    def get_time_in_words(self):
        now = timezone.now()
        if now.date() == self.created.date():
            pass
        
        time_delta = now - self.created
        if time_delta.days == 0:
            minutes = (time_delta.seconds // 60)
            
            if minutes == 0:
                return "now"

            if minutes > 60:
                hour = (minutes//60)
                return f"{hour} hour ago"
            
            return f"{minutes} mins ago"
        
        return f"{time_delta.days} days ago"


class ChatMessageFile(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          editable=False, default=uuid_without_dash)
    message = models.ForeignKey(
        ChatMessage, on_delete=models.SET_NULL, null=True, related_name="files")
    file = models.CharField(max_length=20400, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    

class UserOnlineStatus(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="online_status")
    online = models.BooleanField(default=True)
    # timestamp = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        onlineMsg = "online" if self.online else "offline"
        return f"{self.user} {onlineMsg}"
