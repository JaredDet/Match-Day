import logging
from dataclasses import dataclass
from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.constants import MATCH_LINEUP_SIZE
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LineupPlayerInput:
    player_id: UUID
    shirt_number: int


class SetMatchLineupUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        lineup_repository: MatchSquadRepository,
        player_repository: PlayerRepository,
    ):
        self.match_repository = match_repository
        self.lineup_repository = lineup_repository
        self.player_repository = player_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        team_side: TeamSide,
        formation: MatchFormation,
        players: list[LineupPlayerInput],
        substitutes: list[LineupPlayerInput] | None = None,
        captain_id: UUID | None = None,
    ) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        if match.status != MatchStatus.SCHEDULED:
            raise MatchErrors.InvalidState
        if len(players) != MATCH_LINEUP_SIZE:
            raise MatchErrors.InvalidLineupSize
        resolved_substitutes = substitutes or []
        squad = players + resolved_substitutes
        starter_ids = [player.player_id for player in players]
        player_ids = [player.player_id for player in squad]
        if len(player_ids) != len(set(player_ids)):
            raise MatchErrors.DuplicateLineupPlayer
        shirt_numbers = [player.shirt_number for player in squad]
        if len(shirt_numbers) != len(set(shirt_numbers)):
            raise MatchErrors.DuplicateLineupShirt

        found_players = self.player_repository.get_many(player_ids)
        if len(found_players) != len(player_ids):
            raise TeamErrors.PlayerNotFound

        expected_team_id = match.home_team_id if team_side == TeamSide.HOME else match.away_team_id
        if any(player.team_id != expected_team_id for player in found_players.values()):
            raise MatchErrors.InvalidPlayerTeam

        team = match.home_team if team_side == TeamSide.HOME else match.away_team
        resolved_captain_id = captain_id or team.captain_id
        if captain_id is not None and captain_id not in starter_ids:
            raise MatchErrors.InvalidLineupCaptain
        if resolved_captain_id not in starter_ids:
            logger.warning(
                "La alineación del partido %s no tiene capitán para el equipo %s (%s); "
                "requiere revisión",
                match.id,
                team.id,
                team_side,
            )
            resolved_captain_id = None

        squad_players = [
            match.add_squad_player(
                player=found_players[player.player_id],
                shirt_number=player.shirt_number,
                role=MatchSquadRole.STARTER,
                is_captain=player.player_id == resolved_captain_id,
            )
            for player in players
        ]
        squad_players.extend(
            match.add_squad_player(
                player=found_players[player.player_id],
                shirt_number=player.shirt_number,
                role=MatchSquadRole.SUBSTITUTE,
            )
            for player in resolved_substitutes
        )
        match.set_formation(team_side=team_side, formation=formation)
        self.match_repository.save(match)
        self.lineup_repository.replace(
            match_id=match.id,
            team_side=team_side,
            players=squad_players,
        )
