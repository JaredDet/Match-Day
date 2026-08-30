from dataclasses import dataclass
from uuid import UUID

from modules.matches.domain.match import MatchFormation


@dataclass(frozen=True, slots=True)
class TeamDetail:
    id: UUID
    name: str
    goals: int
    formation: MatchFormation | None
