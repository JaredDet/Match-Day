from dataclasses import dataclass
from uuid import UUID

from injector import inject

from modules.tournaments.infrastructure.query_repository.tournament_query_repository import (
    TournamentQueryRepository,
)


@dataclass(frozen=True, slots=True)
class TournamentSummary:
    id: UUID
    slug: str
    name: str
    country: str
    category: str
    max_teams_per_group: int


class ListTournamentsQuery:
    @inject
    def __init__(self, tournament_query_repository: TournamentQueryRepository):
        self.tournament_query_repository = tournament_query_repository

    def execute(self) -> tuple[TournamentSummary, ...]:
        return self.tournament_query_repository.list()
