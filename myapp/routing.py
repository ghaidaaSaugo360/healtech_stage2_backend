from django.urls import path
 
from . import consumers, whatsapp_consumers
 
websocket_urlpatterns = [
    path('ws/<int:room_name>/', consumers.ChatConsumer.as_asgi()),
     path('ws/whatsapp/', whatsapp_consumers.WhatsAppConsumer.as_asgi()),
]