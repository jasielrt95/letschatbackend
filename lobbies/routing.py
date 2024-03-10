from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/lobbies/<str:lobby_id>/", consumers.LobbyConsumer.as_asgi()),
]
