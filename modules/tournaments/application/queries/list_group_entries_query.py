from dataclasses import dataclass
from uuid import UUID

from injector import inject

from modules.tournaments.infrastructure.query_repository.group_entry_query_repository import (
    GroupEntryQueryRepository,
)


@dataclass(frozen=True, slots=True)
class GroupEntrySummary:
    id: UUID
    group_id: UUID
    team_id: UUID


class ListGroupEntriesQuery:
    @inject
    def __init__(self, group_entry_query_repository: GroupEntryQueryRepository):
        self.group_entry_query_repository = group_entry_query_repository

    def execute(self, *, group_id: UUID | None = None) -> tuple[GroupEntrySummary, ...]:
        return self.group_entry_query_repository.list(group_id=group_id)
