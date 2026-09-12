from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import MatchStatus
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.injury_repository import InjuryRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository


class RegisterInjuryUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        injury_repository: InjuryRepository,
        player_repository: PlayerRepository,
        squad_repository: MatchSquadRepository,
    ):
        self.match_repository = match_repository
        self.injury_repository = injury_repository
        self.player_repository = player_repository
        self.squad_repository = squad_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        player_id: UUID,
        minute: int,
        added_minute: int = 0,
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        if match.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState

        player = self.player_repository.get(player_id)

        if player is None:
            raise TeamErrors.PlayerNotFound

        squad_player = self.squad_repository.get_for_update(
            match_id=match.id,
            player_id=player.id,
        )

        if squad_player is None or not squad_player.is_on_field:
            if squad_player is not None and squad_player.is_sent_off:
                raise MatchErrors.PlayerSentOff

            raise MatchErrors.PlayerNotOnField

        injury = match.register_injury(
            player=player,
            minute=minute,
            added_minute=added_minute,
        )

        self.injury_repository.save(injury)

        return injury.id
