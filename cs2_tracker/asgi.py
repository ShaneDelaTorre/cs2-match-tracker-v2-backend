import os
import django
from django.core.asgi import get_asgi_application

# 1. Set environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs2_tracker.settings')

# 2. Initialize Django (creates the 'http' app)
django_asgi_app = get_asgi_application()

# 3. NOW import your Channels-specific code
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chat.consumers import ChatConsumer
from chat.middleware import JWTAuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<int:user_id>/", ChatConsumer.as_asgi())
        ])
    )
})
