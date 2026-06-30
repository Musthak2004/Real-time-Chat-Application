import asyncio
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Conversation
from chat_messages.models import Message
from notifications.tasks import create_notification


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        if not await self._is_participant():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):

        data = json.loads(text_data)
        content = data.get("content", "").strip()

        if not content:
            return

        message = await self._save_message(content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": message.id,
                "sender_id": self.user.id,
                "sender_username": self.user.username,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            },
        )

        asyncio.ensure_future(
            asyncio.to_thread(
                create_notification.delay,
                conversation_id=self.conversation_id,
                sender_id=self.user.id,
                sender_username=self.user.username,
                content=content,
            )
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _is_participant(self):

        return Conversation.objects.filter(
            pk=self.conversation_id,
            participants=self.user,
        ).exists()

    @database_sync_to_async
    def _save_message(self, content):

        return Message.objects.create(
            conversation_id=self.conversation_id,
            sender=self.user,
            content=content,
            message_type="TEXT",
        )
