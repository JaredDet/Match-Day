from dataclasses import dataclass
from uuid import UUID

from injector import inject

from modules.tournaments.infrastructure.query_repository.season_query_repository import (
    SeasonQueryRepository,
)


@dataclass(frozen=True, slots=True)
class SeasonSummary:
    id: UUID
    tournament_id: UUID
    name: str
    team_ids: tuple[UUID, ...]


class ListSeasonsQuery:
    @inject
    def __init__(self, season_query_repository: SeasonQueryRepository):
        self.season_query_repository = season_query_repository

    def execute(self, *, tournament_id: UUID | None = None) -> tuple[SeasonSummary, ...]:
        return self.season_query_repository.list(tournament_id=tournament_id)
