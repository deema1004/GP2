from django.contrib import admin
from chat.models import ChatRoom, ChatMessage, UserOnlineStatus


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ["user1", "user2", ]


admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(UserOnlineStatus)
