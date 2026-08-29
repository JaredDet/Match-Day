from uuid import UUID

from injector import inject

from modules.matches.application.queries.match_detail import MatchDetail
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)


class GetMatchQuery:
    @inject
    def __init__(self, match_query_repository: MatchQueryRepository):
        self.match_query_repository = match_query_repository

    def execute(self, match_id: UUID) -> MatchDetail:
        match = self.match_query_repository.get(match_id)
        if match is None:
            raise MatchErrors.NotFound
        return match
