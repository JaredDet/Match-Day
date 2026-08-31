from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from injector import inject

from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)


class MatchEventType(StrEnum):
    GOAL = "goal"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"


@dataclass(frozen=True, slots=True)
class MatchEventDetail:
    id: UUID
    type: MatchEventType
    team_side: TeamSide
    player_id: UUID
    player_name: str
    minute: int


@dataclass(frozen=True, slots=True)
class MatchSquadPlayerDetail:
    player_id: UUID
    player_name: str
    team_side: TeamSide
    shirt_number: int
    role: MatchSquadRole
    is_captain: bool


@dataclass(frozen=True, slots=True)
class MatchTeamDetail:
    id: UUID
    name: str
    goals: int
    formation: MatchFormation | None
    lineup: tuple[MatchSquadPlayerDetail, ...]


@dataclass(frozen=True, slots=True)
class MatchDetail:
    id: UUID
    status: MatchStatus
    scheduled_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    stadium_name: str | None
    referee_name: str | None
    home_team: MatchTeamDetail
    away_team: MatchTeamDetail
    events: tuple[MatchEventDetail, ...]


class GetMatchQuery:
    @inject
    def __init__(self, match_query_repository: MatchQueryRepository):
        self.match_query_repository = match_query_repository

    def execute(self, match_id: UUID) -> MatchDetail:
        match = self.match_query_repository.get(match_id)
        if match is None:
            raise MatchErrors.NotFound
        return match
