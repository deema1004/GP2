from rest_framework.generics import ListAPIView
from ..models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError as RestValidationError
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


class RoomListAPIView(ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        qs = user.rooms.all()
        return qs


class ChatRoomMessageListAPIView(ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated, ]
    lookup_url_kwarg = "room_id"

    def get_queryset(self):
        user = self.request.user
        room = self.get_room()
        qs = room.messages.all().order_by("-created")
        return qs

    def get_room(self):
        room_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            qs = ChatRoom.objects.filter(id=room_id)
            if not qs.exists():
                raise NotFound("Chat-Room does not exists with this id")
        except ValidationError as e:
            raise NotFound(e)

        return qs.get()


@api_view(["POST", ])
@permission_classes([IsAuthenticated, ])
def message_create_api_view(request):
    data = request.data
    user_id = data.get("user_id")
    room = ChatRoom.objects.get_or_create_room(request.user, user_id)
    message = data.get("message")
    message_obj = room.messages.create(user=request.user, message=message)
    serializer = ChatMessageSerializer(instance=message_obj)
    serializer.context["request"] = request
    return Response(serializer.data)


@api_view(["POST", ])
@permission_classes([IsAuthenticated, ])
def create_room_api_view(request):
    data = request.data
    user_id = data.get("user_id")
    room = ChatRoom.objects.get_or_create_room(request.user, user_id)
    serializer = ChatRoomSerializer(instance=room)
    serializer.context["request"] = request
    return Response(serializer.data)
