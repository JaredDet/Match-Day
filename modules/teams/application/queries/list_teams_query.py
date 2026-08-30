from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from injector import inject

from modules.teams.infrastructure.query_repository.team_query_repository import (
    TeamQueryRepository,
)


class TeamMatchResult(StrEnum):
    WIN = "win"
    DRAW = "draw"
    LOSS = "loss"


@dataclass(frozen=True, slots=True)
class TeamLastMatch:
    match_id: UUID
    opponent_name: str
    goals_for: int
    goals_against: int
    result: TeamMatchResult


@dataclass(frozen=True, slots=True)
class TeamNextMatch:
    match_id: UUID
    opponent_name: str
    scheduled_at: datetime


@dataclass(frozen=True, slots=True)
class TeamSummary:
    id: UUID
    name: str
    last_match: TeamLastMatch | None
    next_match: TeamNextMatch | None


class ListTeamsQuery:
    @inject
    def __init__(self, team_query_repository: TeamQueryRepository):
        self.team_query_repository = team_query_repository

    def execute(self, *, search: str | None = None) -> tuple[TeamSummary, ...]:
        return self.team_query_repository.list(search=search)
