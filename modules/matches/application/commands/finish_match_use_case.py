from datetime import datetime
from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class FinishMatchUseCase:
    @inject
    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    @transaction.atomic
    def execute(self, match_id: UUID, *, finished_at: datetime | None = None) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        match.finish(finished_at)
        self.match_repository.save(match)
