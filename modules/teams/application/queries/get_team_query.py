from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from modules.teams.application.queries.list_teams_query import TeamMatchResult
from modules.teams.domain.player import PlayerPosition
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.query_repository.team_query_repository import (
    TeamQueryRepository,
)


@dataclass(frozen=True, slots=True)
class TeamStatistics:
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int


@dataclass(frozen=True, slots=True)
class TeamPlayerDetail:
    id: UUID
    name: str
    preferred_position: PlayerPosition | None
    preferred_shirt_number: int | None
    is_captain: bool


@dataclass(frozen=True, slots=True)
class TeamRecentMatch:
    match_id: UUID
    opponent_name: str
    scheduled_at: datetime
    goals_for: int
    goals_against: int
    result: TeamMatchResult


@dataclass(frozen=True, slots=True)
class TeamDetail:
    id: UUID
    name: str
    statistics: TeamStatistics
    players: tuple[TeamPlayerDetail, ...]
    recent_matches: tuple[TeamRecentMatch, ...]


class GetTeamQuery:
    @inject
    def __init__(self, team_query_repository: TeamQueryRepository):
        self.team_query_repository = team_query_repository

    def execute(self, team_id: UUID) -> TeamDetail:
        team = self.team_query_repository.get(team_id)
        if team is None:
            raise TeamErrors.NotFound
        return team
