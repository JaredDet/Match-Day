from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.penalty_shootout import PenaltyShootout
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.penalty_shootout_repository import (
    PenaltyShootoutRepository,
)


class StartPenaltyShootoutUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        shootout_repository: PenaltyShootoutRepository,
    ):
        self.match_repository = match_repository
        self.shootout_repository = shootout_repository

    @transaction.atomic
    def execute(self, *, match_id: UUID) -> UUID:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        if self.shootout_repository.exists(match.id):
            raise MatchErrors.PenaltyShootoutAlreadyExists

        shootout = PenaltyShootout.start(match=match)

        self.shootout_repository.save(shootout)

        return shootout.id
