from datetime import datetime
from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.penalty_shootout_repository import (
    PenaltyShootoutRepository,
)


class FinishPenaltyShootoutUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        shootout_repository: PenaltyShootoutRepository,
    ):
        self.match_repository = match_repository
        self.shootout_repository = shootout_repository

    @transaction.atomic
    def execute(self, *, match_id: UUID, finished_at: datetime | None = None) -> None:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        shootout = self.shootout_repository.get_for_update(match.id)

        if shootout is None:
            raise MatchErrors.PenaltyShootoutNotFound

        shootout.finish(finished_at)
        match.finish(finished_at)

        self.shootout_repository.save(shootout)
        self.match_repository.save(match)
