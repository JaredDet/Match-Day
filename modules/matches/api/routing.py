from django.urls import path

from modules.matches.api.consumers import MatchClockConsumer

websocket_urlpatterns = [
    path("ws/matches/<uuid:match_id>/clock/", MatchClockConsumer.as_asgi()),
]
