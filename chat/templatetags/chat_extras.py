from django import template
from chat.models import ChatRoom
from django.contrib.auth import get_user_model

User = get_user_model()

register = template.Library()


@register.simple_tag
def get_to_user(room, user):
	if room is None:
		return None
	
	if isinstance(room, str):
		room = ChatRoom.objects.get(id=room)

	if isinstance(user, str):
		user = User.objects.get(id=user)

	if room.user1 == user:
		to_user = room.user2
		return to_user

	to_user = room.user1
	return to_user


@register.simple_tag
def get_unseen_msgs_count(room, from_user):
	return room.messages.filter(seen=False, user=from_user).count()

