from datetime import datetime
from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.realtime.match_clock_publisher import MatchClockPublisher
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class FinishMatchUseCase:
    @inject
    def __init__(self, match_repository: MatchRepository, clock_publisher=None):
        self.match_repository = match_repository
        self.clock_publisher = clock_publisher or MatchClockPublisher()

    @transaction.atomic
    def execute(self, match_id: UUID, *, finished_at: datetime | None = None) -> None:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        match.finish(finished_at)

        self.match_repository.save(match)

        snapshot = match.clock_snapshot()
        transaction.on_commit(lambda: self.clock_publisher.publish_snapshot(match.id, snapshot))
