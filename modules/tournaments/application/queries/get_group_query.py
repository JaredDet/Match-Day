from uuid import UUID

from injector import inject

from modules.tournaments.application.queries.list_groups_query import GroupSummary
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.group_query_repository import (
    GroupQueryRepository,
)


class GetGroupQuery:
    @inject
    def __init__(self, group_query_repository: GroupQueryRepository):
        self.group_query_repository = group_query_repository

    def execute(self, group_id: UUID) -> GroupSummary:
        result = self.group_query_repository.get(group_id)

        if result is None:
            raise TournamentErrors.GroupNotFound

        return result
