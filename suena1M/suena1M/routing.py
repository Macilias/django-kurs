from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<slug>[a-zA-Z0-9\.-_]+)/$", consumers.GameConsumer.as_asgi()),
]
