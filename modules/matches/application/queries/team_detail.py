from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TeamDetail:
    name: str
    goals: int
