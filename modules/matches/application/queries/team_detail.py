from dataclasses import dataclass
from uuid import UUID

from modules.matches.domain.goal import GoalType
from modules.matches.domain.match import MatchFormation
from modules.matches.domain.match_event import TeamSide


@dataclass(frozen=True, slots=True)
class MatchGoalPreview:
    player_name: str
    goal_type: GoalType
    minute: int
    added_minute: int


@dataclass(frozen=True, slots=True)
class TeamDetail:
    id: UUID
    name: str
    team_side: TeamSide
    score: int
    penalty_score: int | None
    formation: MatchFormation | None
    goals: tuple[MatchGoalPreview, ...]
