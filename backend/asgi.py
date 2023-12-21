import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
from django.core.asgi import get_asgi_application
 
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
 
import myapp.routing
 
 
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            myapp.routing.websocket_urlpatterns
        )
    )
})