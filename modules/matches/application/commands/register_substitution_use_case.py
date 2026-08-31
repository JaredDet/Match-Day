from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_substitution import MatchSubstitution
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.matches.infrastructure.repository.match_substitution_repository import (
    MatchSubstitutionRepository,
)


class RegisterSubstitutionUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        squad_repository: MatchSquadRepository,
        substitution_repository: MatchSubstitutionRepository,
    ):
        self.match_repository = match_repository
        self.squad_repository = squad_repository
        self.substitution_repository = substitution_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        player_out_id: UUID,
        player_in_id: UUID,
        minute: int,
        added_minute: int = 0,
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        if match.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState

        player_out = self.squad_repository.get_for_update(
            match_id=match.id,
            player_id=player_out_id,
        )
        player_in = self.squad_repository.get_for_update(
            match_id=match.id,
            player_id=player_in_id,
        )
        if player_out is None or player_in is None:
            raise MatchErrors.InvalidSubstitutionPlayers
        if self.substitution_repository.has_entered(player_in.id):
            raise MatchErrors.InvalidSubstitutePlayer

        substitution = MatchSubstitution.create(
            match=match,
            player_out=player_out,
            player_in=player_in,
            minute=minute,
            added_minute=added_minute,
        )
        self.squad_repository.save_all([player_out, player_in])
        self.substitution_repository.save(substitution)
        return substitution.id
