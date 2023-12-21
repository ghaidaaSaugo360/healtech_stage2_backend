import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WhatsAppConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Join the group for receiving notifications
        await self.channel_layer.group_add("whatsapp_group", self.channel_name)

    async def disconnect(self, close_code):
        # Leave the group when the connection is closed
        await self.channel_layer.group_discard("whatsapp_group", self.channel_name)

    async def notify_whatsapp_event(self, event):
        # Send the received event data to the WebSocket client
        await self.send(text_data=json.dumps({
            'whatsapp_event': event.get('message', 'Default WhatsApp event message'),
           # 'user_id': event.get('user_id'),  # Include user ID in the WebSocket message
            'patient_id': event.get('patient_id'),  # Include patient ID in the WebSocket message
        }))
