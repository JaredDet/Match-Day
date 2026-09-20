from uuid import UUID

from injector import inject

from modules.tournaments.application.queries.list_group_entries_query import GroupEntrySummary
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.group_entry_query_repository import (
    GroupEntryQueryRepository,
)


class GetGroupEntryQuery:
    @inject
    def __init__(self, group_entry_query_repository: GroupEntryQueryRepository):
        self.group_entry_query_repository = group_entry_query_repository

    def execute(self, group_entry_id: UUID) -> GroupEntrySummary:
        result = self.group_entry_query_repository.get(group_entry_id)

        if result is None:
            raise TournamentErrors.GroupEntryNotFound

        return result
