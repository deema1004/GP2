from rest_framework import serializers
from ..models import ChatRoom, ChatMessage, ChatMessageFile
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "profile_image"]
    
    def get_profile_image(self, serializer):
        return settings.RUNNING_DOMAIN_ORIGIN + serializer.get_profile_image().url


class ChatMessageFileSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(read_only=True)
    message = serializers.StringRelatedField(read_only=True)
    file = serializers.StringRelatedField(read_only=True)
    extension = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessageFile
        fields = "__all__"

    def get_extension(self, serializer):

        return ".jpg"


class ChatMessageSerializer(serializers.ModelSerializer):
    room = serializers.StringRelatedField(read_only=True)
    user = UserSerializer(read_only=True)
    files = ChatMessageFileSerializer(read_only=True, many=True)
    is_me = serializers.SerializerMethodField()
    get_time = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = "__all__"

    def get_is_me(self, serializer):
        request = self.context.get("request")
        return serializer.user == request.user

    def get_get_time(self, serializer):
        return serializer.get_time_in_words()


class ChatRoomSerializer(serializers.ModelSerializer):
    event = serializers.StringRelatedField()
    last_message = serializers.SerializerMethodField()
    last_unseen_messages_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        # fields = "__all__"
        exclude = ["modified"]

    def get_last_unseen_messages_count(self, obj):

        return 0

    def get_last_message(self, obj):
        last_message = obj.messages.order_by("-created").first()
        if last_message is None:
            return None

        serialized = ChatMessageSerializer(last_message).data
        return serialized


"""
isMe
related_ad serialized
room serialized

"""

