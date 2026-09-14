from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from modules.matches.domain.match_clock import MatchClockSnapshot


def match_clock_group_name(match_id) -> str:
    return f"match.clock.{match_id}"


def serialize_clock_snapshot(snapshot: MatchClockSnapshot) -> dict:
    return {
        "period": snapshot.period.value if snapshot.period is not None else None,
        "status": snapshot.status.value,
        "minute": snapshot.minute,
        "second": snapshot.second,
        "added_minute": snapshot.added_minute,
        "elapsed_seconds": snapshot.elapsed_seconds,
        "remaining_seconds": snapshot.remaining_seconds,
        "deadline_at": (
            snapshot.deadline_at.isoformat() if snapshot.deadline_at is not None else None
        ),
        "announced_added_minutes": snapshot.announced_added_minutes,
        "version": snapshot.version,
        "as_of": snapshot.as_of.isoformat(),
    }


class MatchClockPublisher:
    def publish_snapshot(self, match_id, snapshot: MatchClockSnapshot) -> None:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        async_to_sync(channel_layer.group_send)(
            match_clock_group_name(match_id),
            {
                "type": "match.clock.snapshot",
                "payload": {
                    "type": "match.clock.snapshot",
                    "match_id": str(match_id),
                    "clock": serialize_clock_snapshot(snapshot),
                },
            },
        )

    def publish_alert(self, match_id, alert: str, snapshot: MatchClockSnapshot) -> None:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        async_to_sync(channel_layer.group_send)(
            match_clock_group_name(match_id),
            {
                "type": "match.clock.alert",
                "payload": {
                    "type": "match.clock.alert",
                    "match_id": str(match_id),
                    "alert": alert,
                    "clock": serialize_clock_snapshot(snapshot),
                },
            },
        )
