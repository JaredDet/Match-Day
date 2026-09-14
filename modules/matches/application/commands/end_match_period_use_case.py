from datetime import datetime
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.matches.domain.match_event import MatchPeriod
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.realtime.match_clock_publisher import MatchClockPublisher
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class EndMatchPeriodUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        clock_publisher: MatchClockPublisher,
    ):
        self.match_repository = match_repository
        self.clock_publisher = clock_publisher

    @transaction.atomic
    def execute(
        self,
        match_id: UUID,
        expected_period: MatchPeriod,
        *,
        ended_at: datetime | None = None,
    ) -> None:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        match.end_period(
            expected_period=expected_period,
            ended_at=ended_at or timezone.now(),
        )
        self.match_repository.save(match)

        snapshot = match.clock_snapshot()
        transaction.on_commit(lambda: self.clock_publisher.publish_snapshot(match.id, snapshot))
