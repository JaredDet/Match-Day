from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from modules.tournaments.domain.group_entry import GroupEntry

if TYPE_CHECKING:
    from modules.tournaments.application.queries.list_group_entries_query import GroupEntrySummary


class GroupEntryQueryRepository:
    def get(self, group_entry_id: UUID) -> GroupEntrySummary | None:
        entity = GroupEntry.objects.all().order_by("id").filter(id=group_entry_id).first()

        return self._summary(entity) if entity is not None else None

    def list(self, *, group_id: UUID | None = None) -> tuple[GroupEntrySummary, ...]:
        queryset = GroupEntry.objects.all().order_by("id")

        if group_id is not None:
            queryset = queryset.filter(group_id=group_id)

        return tuple(self._summary(entity) for entity in queryset)

    @staticmethod
    def _summary(entity: GroupEntry) -> GroupEntrySummary:
        from modules.tournaments.application.queries.list_group_entries_query import (
            GroupEntrySummary,
        )

        return GroupEntrySummary(id=entity.id, group_id=entity.group_id, team_id=entity.team_id)
