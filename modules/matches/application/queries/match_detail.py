from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide


class MatchEventType(StrEnum):
    GOAL = "goal"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"


@dataclass(frozen=True, slots=True)
class TeamDetail:
    name: str
    goals: int


@dataclass(frozen=True, slots=True)
class MatchEventDetail:
    id: UUID
    type: MatchEventType
    team_side: TeamSide
    player_name: str
    minute: int


@dataclass(frozen=True, slots=True)
class MatchDetail:
    id: UUID
    status: MatchStatus
    scheduled_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    home_team: TeamDetail
    away_team: TeamDetail
    events: tuple[MatchEventDetail, ...]
