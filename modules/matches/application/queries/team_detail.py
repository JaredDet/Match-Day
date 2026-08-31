from dataclasses import dataclass
from uuid import UUID

from modules.matches.domain.match import MatchFormation
from modules.matches.domain.match_event import TeamSide


@dataclass(frozen=True, slots=True)
class TeamDetail:
    id: UUID
    name: str
    team_side: TeamSide
    goals: int
    formation: MatchFormation | None
