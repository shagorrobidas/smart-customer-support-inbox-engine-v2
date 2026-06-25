import json
import asyncio
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from conversations.services.ai import AISuggetionsService


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', text_data)
        except (json.JSONDecodeError, TypeError):
            message = text_data

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )


        # Generate the suggestion based on the user's message
        ai_reply_text = AISuggetionsService.suggest_reply(message)

        # Simulate a realistic typing/processing delay of 500ms
        await asyncio.sleep(0.5)

        # Broadcast the AI reply to the room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {
                    'sender': 'agent',
                    'message': f" {ai_reply_text}",
                    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
                }
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        """
        Invoked when a message is broadcast to the group via the channel layer.
        Sends the message data down to the connected WebSocket client.
        """
        message = event['message']

        # Send message content to WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': message
        }))


def broadcast_message(conversation_id, message_data):

    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f"chat_{conversation_id}",
                {
                    "type": "chat_message",
                    "message": message_data
                }
            )
        except Exception:
            # Log or handle channel layer exceptions gracefully in development
            pass