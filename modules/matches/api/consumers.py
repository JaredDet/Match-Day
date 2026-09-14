from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from modules.matches.domain.match import Match
from modules.matches.infrastructure.realtime.match_clock_publisher import (
    match_clock_group_name,
    serialize_clock_snapshot,
)


class MatchClockConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        self.group_name = match_clock_group_name(self.match_id)
        snapshot = await self._get_snapshot()

        if snapshot is None:
            await self.close(code=4404)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json(
            {
                "type": "match.clock.snapshot",
                "match_id": str(self.match_id),
                "clock": snapshot,
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def match_clock_snapshot(self, event):
        await self.send_json(event["payload"])

    async def match_clock_alert(self, event):
        await self.send_json(event["payload"])

    @database_sync_to_async
    def _get_snapshot(self):
        match = Match.objects.filter(id=self.match_id).first()
        if match is None:
            return None
        return serialize_clock_snapshot(match.clock_snapshot())
