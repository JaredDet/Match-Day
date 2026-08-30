from dataclasses import dataclass
from uuid import UUID

from injector import inject

from modules.teams.infrastructure.query_repository.player_query_repository import (
    PlayerQueryRepository,
)


@dataclass(frozen=True, slots=True)
class PlayerTeamSummary:
    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class PlayerSummary:
    id: UUID
    name: str
    team: PlayerTeamSummary
    is_captain: bool
    appearances: int
    goals: int


class ListPlayersQuery:
    @inject
    def __init__(self, player_query_repository: PlayerQueryRepository):
        self.player_query_repository = player_query_repository

    def execute(
        self,
        *,
        search: str | None = None,
        team_id: UUID | None = None,
    ) -> tuple[PlayerSummary, ...]:
        return self.player_query_repository.list(search=search, team_id=team_id)
