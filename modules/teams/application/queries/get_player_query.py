from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from modules.teams.application.queries.list_teams_query import TeamMatchResult
from modules.teams.domain.player import PlayerPosition
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.query_repository.player_query_repository import (
    PlayerQueryRepository,
)


@dataclass(frozen=True, slots=True)
class PlayerTeamDetail:
    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class PlayerStatistics:
    appearances: int
    goals: int
    yellow_cards: int
    red_cards: int


@dataclass(frozen=True, slots=True)
class PlayerRecentMatch:
    match_id: UUID
    scheduled_at: datetime
    opponent: PlayerTeamDetail
    result: TeamMatchResult
    goals: int
    yellow_cards: int
    red_cards: int


@dataclass(frozen=True, slots=True)
class PlayerDetail:
    id: UUID
    name: str
    preferred_position: PlayerPosition | None
    preferred_shirt_number: int | None
    team: PlayerTeamDetail
    is_captain: bool
    statistics: PlayerStatistics
    recent_matches: tuple[PlayerRecentMatch, ...]


class GetPlayerQuery:
    @inject
    def __init__(self, player_query_repository: PlayerQueryRepository):
        self.player_query_repository = player_query_repository

    def execute(self, player_id: UUID) -> PlayerDetail:
        player = self.player_query_repository.get(player_id)
        if player is None:
            raise TeamErrors.PlayerNotFound
        return player
