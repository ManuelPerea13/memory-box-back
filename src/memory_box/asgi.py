import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import orders.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_box.settings')

django_asgi = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi,
    'websocket': URLRouter(orders.routing.websocket_urlpatterns),
})
