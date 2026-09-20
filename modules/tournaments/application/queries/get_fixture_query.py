from uuid import UUID

from injector import inject

from modules.tournaments.application.queries.list_fixtures_query import FixtureSummary
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.fixture_query_repository import (
    FixtureQueryRepository,
)


class GetFixtureQuery:
    @inject
    def __init__(self, fixture_query_repository: FixtureQueryRepository):
        self.fixture_query_repository = fixture_query_repository

    def execute(self, fixture_id: UUID) -> FixtureSummary:
        result = self.fixture_query_repository.get(fixture_id)

        if result is None:
            raise TournamentErrors.FixtureNotFound

        return result
