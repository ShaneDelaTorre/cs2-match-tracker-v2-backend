from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from chat.services import send_message, get_conversation
from accounts.services import are_friends

class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
        other_user = await get_user_by_id(self.other_user_id)

        if other_user is None:
            await self.close()
            return

        friends = await check_friends(self.user, other_user)
        if not friends:
            await self.close()
            return

        room_ids = sorted([self.user.id, int(self.other_user_id)])
        self.room_group_name = f"chat_{room_ids[0]}_{room_ids[1]}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        history = await get_history(self.user, other_user)
        await self.send_json({"type": "history", "messages": history})

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive_json(self, content):
        body = content.get("body", "").strip()
        if not body:
            return

        other_user = await get_user_by_id(self.other_user_id)
        message = await save_message(self.user, other_user, body)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message_id": message.id,
                "sender_id": self.user.id,
                "body": message.body,
                "sent_at": message.sent_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send_json({
            "type": "message",
            "message_id": event["message_id"],
            "sender_id": event["sender_id"],
            "body": event["body"],
            "sent_at": event["sent_at"],
        })


@database_sync_to_async
def get_user_by_id(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

@database_sync_to_async
def check_friends(user_a, user_b):
    return are_friends(user_a, user_b)

@database_sync_to_async
def save_message(sender, receiver, body):
    return send_message(sender, receiver, body)

@database_sync_to_async
def get_history(user_a, user_b):
    messages = get_conversation(user_a, user_b)
    return [
        {
            "message_id": m.id,
            "sender_id": m.sender_id,
            "body": m.body,
            "sent_at": m.sent_at.isoformat(),
        }
        for m in messages
    ]