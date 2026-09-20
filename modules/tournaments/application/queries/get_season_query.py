from uuid import UUID

from injector import inject

from modules.tournaments.application.queries.list_seasons_query import SeasonSummary
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.season_query_repository import (
    SeasonQueryRepository,
)


class GetSeasonQuery:
    @inject
    def __init__(self, season_query_repository: SeasonQueryRepository):
        self.season_query_repository = season_query_repository

    def execute(self, season_id: UUID) -> SeasonSummary:
        result = self.season_query_repository.get(season_id)

        if result is None:
            raise TournamentErrors.SeasonNotFound

        return result
