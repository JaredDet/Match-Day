from uuid import UUID

from injector import inject

from modules.tournaments.application.queries.list_fixtures_query import FixtureSummary
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.fixture_query_repository import (
    FixtureQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.season_query_repository import (
    SeasonQueryRepository,
)


class ListSeasonFixturesQuery:
    @inject
    def __init__(
        self,
        season_query_repository: SeasonQueryRepository,
        fixture_query_repository: FixtureQueryRepository,
    ):
        self.season_query_repository = season_query_repository
        self.fixture_query_repository = fixture_query_repository

    def execute(self, season_id: UUID) -> tuple[FixtureSummary, ...]:
        if self.season_query_repository.get(season_id) is None:
            raise TournamentErrors.SeasonNotFound

        return self.fixture_query_repository.list_for_season(season_id)
