from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TeamDetail:
    id: UUID
    name: str
    goals: int
