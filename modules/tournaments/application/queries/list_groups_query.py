from dataclasses import dataclass
from uuid import UUID

from injector import inject

from modules.tournaments.infrastructure.query_repository.group_query_repository import (
    GroupQueryRepository,
)


@dataclass(frozen=True, slots=True)
class GroupSummary:
    id: UUID
    phase_id: UUID
    name: str
    tie_break_order: tuple[UUID, ...]


class ListGroupsQuery:
    @inject
    def __init__(self, group_query_repository: GroupQueryRepository):
        self.group_query_repository = group_query_repository

    def execute(self, *, phase_id: UUID | None = None) -> tuple[GroupSummary, ...]:
        return self.group_query_repository.list(phase_id=phase_id)
