from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.matches.domain.match_clock import (
    MatchClockStatus,
    period_clock_values,
)
from modules.matches.infrastructure.realtime.match_clock_publisher import MatchClockPublisher
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class SynchronizeMatchClocksUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        clock_publisher: MatchClockPublisher,
    ):
        self.match_repository = match_repository
        self.clock_publisher = clock_publisher

    def execute(self) -> int:
        synchronized = 0
        for match_id in self.match_repository.list_running_clock_ids():
            self._synchronize_match(match_id)
            synchronized += 1
        return synchronized

    @transaction.atomic
    def _synchronize_match(self, match_id) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None or match.period_ended_at is not None:
            return

        now = timezone.now()
        snapshot = match.clock_snapshot(now)
        _, _, regulation_seconds = period_clock_values(snapshot.period)
        alerts = []

        if (
            match.announced_added_minutes > 0
            and snapshot.elapsed_seconds >= regulation_seconds
            and match.regulation_time_alerted_at is None
        ):
            match.regulation_time_alerted_at = now
            alerts.append("regulation_time_reached")

        if (
            snapshot.status == MatchClockStatus.DEADLINE_REACHED
            and match.period_deadline_alerted_at is None
        ):
            match.period_deadline_alerted_at = now
            alerts.append("period_deadline_reached")

        if alerts:
            self.match_repository.save(match)

        transaction.on_commit(lambda: self._publish(match.id, snapshot, tuple(alerts)))

    def _publish(self, match_id, snapshot, alerts: tuple[str, ...]) -> None:
        self.clock_publisher.publish_snapshot(match_id, snapshot)
        for alert in alerts:
            self.clock_publisher.publish_alert(match_id, alert, snapshot)
