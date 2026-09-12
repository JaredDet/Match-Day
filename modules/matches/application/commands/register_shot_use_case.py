from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import MatchStatus
from modules.matches.domain.shot import ShotOutcome
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.matches.infrastructure.repository.shot_repository import ShotRepository
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository


class RegisterShotUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        shot_repository: ShotRepository,
        player_repository: PlayerRepository,
        squad_repository: MatchSquadRepository,
    ):
        self.match_repository = match_repository
        self.shot_repository = shot_repository
        self.player_repository = player_repository
        self.squad_repository = squad_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        player_id: UUID,
        outcome: ShotOutcome,
        minute: int,
        goalkeeper_id: UUID | None = None,
        added_minute: int = 0,
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound
        if match.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState

        player = self._get_player_on_field(match.id, player_id)
        goalkeeper = (
            self._get_player_on_field(match.id, goalkeeper_id)
            if goalkeeper_id is not None
            else None
        )
        shot = match.register_shot(
            player=player,
            goalkeeper=goalkeeper,
            outcome=outcome,
            minute=minute,
            added_minute=added_minute,
        )

        self.shot_repository.save(shot)
        self.match_repository.save(match)
        return shot.id

    def _get_player_on_field(self, match_id: UUID, player_id: UUID):
        player = self.player_repository.get(player_id)
        if player is None:
            raise TeamErrors.PlayerNotFound

        squad_player = self.squad_repository.get_for_update(
            match_id=match_id,
            player_id=player.id,
        )

        if squad_player is not None and squad_player.is_sent_off:
            raise MatchErrors.PlayerSentOff
        if squad_player is None or not squad_player.is_on_field:
            raise MatchErrors.PlayerNotOnField

        return player
