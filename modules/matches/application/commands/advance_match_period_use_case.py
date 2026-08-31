from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match_event import MatchPeriod
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class AdvanceMatchPeriodUseCase:
    @inject
    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    @transaction.atomic
    def execute(self, match_id: UUID, expected_period: MatchPeriod) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        match.advance_period(expected_period)
        self.match_repository.save(match)
