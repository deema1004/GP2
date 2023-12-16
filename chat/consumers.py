import re
import json
from channels.consumer import AsyncConsumer
from .utils import save_chat_message, make_all_messages_of_user_seen, make_a_message_seen, \
    async_get_chat_room, send_by_websocket
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage, UserOnlineStatus
from django.contrib.auth import get_user_model
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist


User = get_user_model()


def update_user_online_status(self, boolean):
    user = self.scope["user"]
    qs = UserOnlineStatus.objects.filter(user=user)
    try:
        obj = qs.get()
    except MultipleObjectsReturned as e:
        print(e)
        qs.delete()
        obj = UserOnlineStatus.objects.create(user=user)
    except ObjectDoesNotExist:
        obj = UserOnlineStatus.objects.create(user=user)
        
    obj.online = boolean
    obj.save()

    return obj


def check_user_online_status(user):
    print("USER --> ", user)
    qs = UserOnlineStatus.objects.filter(user=user)
    print("ONLINE QS --> ", qs)
    try:
        obj = qs.get()
    except MultipleObjectsReturned as e:
        obj = qs.order_by("-modified").first()
        return obj.online

    except ObjectDoesNotExist:
        return False
    
    return obj.online


class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("[CONNECTED] ", event)

        await self.send({
            "type": "websocket.accept"
        })

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.send({
                "type": "websocket.close"
            })
            return False
        
        # online_stat = await self.check_user_online(user)
        # print("[ONLINE STATUS] --> ", online_stat)
        # if not online_stat:
            # chat_room = f"room_{user.id}"
            
        print(f"CONNECTED AS {user.email}")
        chat_room = f"room_{user.id}"
        print(chat_room)
        self.chat_room = chat_room

        # await self.send({
        #     "type": "websocket.close"
        # })
        # return True

        await self.channel_layer.group_add(
            chat_room,
            self.channel_name,  # UNIQUE CHANNEL NAME
        )
        print("Layer Added")

        obj = await self.create_user_online_status()
        print("Creating Online ", obj)

    @database_sync_to_async
    def create_user_online_status(self):
        return update_user_online_status(self, True)

    @database_sync_to_async
    def make_user_offline(self):
        return update_user_online_status(self, False)
    
    @database_sync_to_async
    def check_user_online(self, user):
        return check_user_online_status(user)

    async def websocket_receive(self, event):
        # print("[RECEIVED] ", event)
        print("\n\n")
        text = event["text"]
        # text = text.replace("\'", "\"")

        data = json.loads(text)
        print(data)

        command = data["command"]

        command_type = {
            "new_message": self.new_message,
            'seen_message': self.seen_message,
            "typing_message": self.typing_message,
        }

        try:
            await command_type[command](data)
        except Exception as e:
            print(f"Error  --> {e}\n")
            await self.send({
                "type": "websocket.close",
            })


    async def typing_message(self, data):
        print("Data --> ", data)
        room_id = data.get("room", None)
        if not room_id:
            raise ValueError("Provide a Room")

        room = await async_get_chat_room(room_id)
        curr_user = self.scope["user"]
        if curr_user not in [room.user1, room.user2]:
            raise ValueError("User not in this room")

        if curr_user == room.user1:
            other_user = room.user2
        else:
            other_user = room.user1

        print(other_user)

        chat_room = f"room_{other_user.id}"
        await self.channel_layer.group_send(
            chat_room,
            {
                "type": "send.typing_message",
                "text": {
                    "typing": True,
                    "room": str(room.id),
                    "user_id": str(curr_user.id),
                    "user_email": str(curr_user.email)
                },
            }
        )

    async def send_typing_message(self, data):
        print("HERE", data)

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(data["text"])
        })

    async def seen_message(self, data):
        message_id = data.get("message_id", None)
        all_message = data.get("all_message", None)
        room_id = data.get("room")
        if (not message_id) and ((all_message == False) or (all_message == None)):
            raise ValueError(
                "Either provide 'message_id' or set 'all_message'")

        if all_message == True:
            await self.make_all_message_seen(room_id)

        else:
            await self.make_a_particular_msg_seen(message_id)

    async def make_a_particular_msg_seen(self, message_id):
        room, message = await make_a_message_seen(message_id)
        user = self.scope["user"]
        other_user = room.user1
        if user == other_user:
            other_user = room.user2

        data = {
            "message_id": message.id,
            "room": room.id,
            "command": "message_obj_seen",
        }

        await self.channel_layer.group_send(
            f"room_{other_user.id}",
            {
                "type": "send.message",
                "text": data
            }
        )

    async def make_all_message_seen(self, room_id):
        user = self.scope["user"]
        room, exists = await make_all_messages_of_user_seen(room_id, user)
        if exists:
            other_user = room.user1
            if user == other_user:
                other_user = room.user2

            data = {
                "command": "seen_all_message",
                "user_id": str(other_user.id),
                "user_email": other_user.email,
                "room": str(room.id)
            }
            print("Here")
            await self.channel_layer.group_send(
                f"room_{other_user.id}",
                {
                    "type": "send.message",
                    "text": data
                }
            )

    async def new_message(self, data):
        print("DATA --> ", data)
        msg_data = {
            "room": data.get("room"),
            "message": data.get("message", None),
            "files": data.get("files", None),
            "user": self.scope["user"],
            "user_id": data.get("user_id"),
            "to_user": data.get("to_user"),
        }

        print("MSG FILES __> ", msg_data.get("files"))

        chat_obj = await save_chat_message(msg_data)
        print("Chat --> ", chat_obj)

        serializer = ChatMessageSerializer(instance=chat_obj)
        serializer.context["curr_user"] = self.scope["user"]
        data = serializer.data
        data["command"] = "new_message"
        room = chat_obj.room
        users = [room.user1, room.user2]

        for user in users:
            chat_room = f"room_{user.id}"

            await self.channel_layer.group_send(
                chat_room,
                {
                    "type": "send.message",
                    "text": data,
                }
            )

    async def send_message(self, event):
        data = event["text"]
        # print(data, "\n\n")
        user_online_status = data.get("user_online_status", None)

        if user_online_status is not None:
            await self.send({
                "type": "websocket.send",
                "text": json.dumps(data)
            })
            return True


        if data.get("command") == "seen_all_message":
            data["seen_all"] = True
            data = json.dumps(data)

            await self.send({
                "type": "websocket.send",
                "text": data
            })

            notification_data = {
                "command": "sound",
                "message": "for seen all message"
            }
            user_id = self.chat_room.split("room_")[1]
            chat_room = f"notification_room_{user_id}"
            print(chat_room, "\n\n")
            await self.channel_layer.group_send(
                chat_room,
                {
                    "type": "send.notification",
                    "text": notification_data
                }
            )

            return True

        sent_user = dict(data["user"])
        data["room"] = str(data["room"])
        print("SENT USER --> ", sent_user)
        curr_user = self.scope["user"]
        if str(curr_user.id) == str(sent_user["id"]):
            is_me = True
        else:
            is_me = False

        data["is_me"] = is_me

        data = json.dumps(data)
        await self.send({
            "type": "websocket.send",
            "text": data
        })

    async def websocket_disconnect(self, event):
        print("[DISCONNECTED] ", event)
        user = self.scope["user"]
        if user.is_authenticated:
            obj = await self.make_user_offline()
            print("Making Offline ", obj)

        "SEND OFFLINE MESSAGE TO THE OTHER USER IN ROOM"


class NotificationConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.send({
                "type": "websocket.close"
            })
            return False
        
        print(f"CONNECTED AS {user.email} NOTIFICATION")

        chat_room = f"notification_room_{user.id}"
        self.chat_room = chat_room

        await self.channel_layer.group_add(
            chat_room,
            self.channel_name,  # UNIQUE CHANNEL NAME
        )
        print("Notification Layer Added")
        await self.create_user_online_status()

    async def websocket_receive(self, event):
        print("[RECEIVED] ", event)
    
    async def send_notification(self, event):
        data = event["text"]
        print(data, "\n\n")

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(data)
        })
        return True

    @database_sync_to_async
    def create_user_online_status(self):
        return update_user_online_status(self, True)

    @database_sync_to_async
    def make_user_offline(self):
        return update_user_online_status(self, False)

    async def websocket_disconnect(self, event):
        print("[DISCONNECTED] ", event)
        user = self.scope["user"]
        if user.is_authenticated:
            obj = await self.make_user_offline()
            print("Making Offline from Notification Consumer", obj)
        
        await self.make_user_offline()
