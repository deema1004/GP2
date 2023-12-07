from django.urls import path
from . import views

urlpatterns = [
    path("room/create-room/", views.create_room_api_view, ),
    path("room/", views.RoomListAPIView.as_view(), name="room-list"),
    path("room/messages/<room_id>/", views.ChatRoomMessageListAPIView.as_view(), name="message-list"),
    path("room/message/create/", views.message_create_api_view), 
]