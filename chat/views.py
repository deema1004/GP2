from django.shortcuts import render
from .models import ChatRoom, ChatMessage, ChatMessageFile
from django.contrib.auth.decorators import login_required


@login_required
def chat_view(request):
	chat_room_qs = ChatRoom.objects.get_user_rooms(request.user)
	first_room_messages_qs = ChatMessage.objects.none()
	room_first_user = None
	if chat_room_qs.exists():
		room = chat_room_qs.first()
		room_first_user = room.user1
		if room_first_user == request.user:
			room_first_user = room.user2

		first_room_messages_qs = room.messages.all().order_by("-created")

	print(first_room_messages_qs)
	context = {
		"chat_rooms": chat_room_qs,
		"messages": first_room_messages_qs,
		"room_first_user": room_first_user
	}
	return render(request, "chat/chat.html", context)

