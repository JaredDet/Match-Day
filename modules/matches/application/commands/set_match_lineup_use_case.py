from dataclasses import dataclass
from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_lineup_repository import (
    MatchLineupRepository,
)
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository


@dataclass(frozen=True, slots=True)
class LineupPlayerInput:
    player_id: UUID
    shirt_number: int
    is_captain: bool


class SetMatchLineupUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        lineup_repository: MatchLineupRepository,
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
    ) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        if match.status != MatchStatus.SCHEDULED:
            raise MatchErrors.InvalidState
        if len(players) != 11:
            raise MatchErrors.InvalidLineupSize
        if sum(player.is_captain for player in players) != 1:
            raise MatchErrors.InvalidLineupCaptain

        player_ids = [player.player_id for player in players]
        if len(player_ids) != len(set(player_ids)):
            raise MatchErrors.DuplicateLineupPlayer
        shirt_numbers = [player.shirt_number for player in players]
        if len(shirt_numbers) != len(set(shirt_numbers)):
            raise MatchErrors.DuplicateLineupShirt

        found_players = self.player_repository.get_many(player_ids)
        if len(found_players) != len(player_ids):
            raise TeamErrors.PlayerNotFound

        expected_team_id = match.home_team_id if team_side == TeamSide.HOME else match.away_team_id
        if any(player.team_id != expected_team_id for player in found_players.values()):
            raise MatchErrors.InvalidPlayerTeam

        lineup_players = [
            match.add_lineup_player(
                player=found_players[player.player_id],
                shirt_number=player.shirt_number,
                is_captain=player.is_captain,
            )
            for player in players
        ]
        match.set_formation(team_side=team_side, formation=formation)
        self.match_repository.save(match)
        self.lineup_repository.replace(
            match_id=match.id,
            team_side=team_side,
            players=lineup_players,
        )
