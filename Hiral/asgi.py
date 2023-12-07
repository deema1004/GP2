import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hiral.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Prod")

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chat.consumers import ChatConsumer
from channels.security.websocket import AllowedHostsOriginValidator
# from chat.middleware import TokenAuthMiddleware
from channels.auth import AuthMiddlewareStack


websocket_urlpatterns = [
    path("message/", ChatConsumer.as_asgi(), ),
]

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})

# ws://127.0.0.1:8000/message/
# http://127
