from injector import inject

from modules.tournaments.application.queries.list_tournaments_query import TournamentSummary
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.tournament_query_repository import (
    TournamentQueryRepository,
)


class GetTournamentQuery:
    @inject
    def __init__(self, tournament_query_repository: TournamentQueryRepository):
        self.tournament_query_repository = tournament_query_repository

    def execute(self, slug: str) -> TournamentSummary:
        result = self.tournament_query_repository.get(slug)

        if result is None:
            raise TournamentErrors.NotFound

        return result
