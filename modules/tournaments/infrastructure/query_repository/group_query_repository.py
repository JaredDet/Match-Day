from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from modules.tournaments.domain.group import Group

if TYPE_CHECKING:
    from modules.tournaments.application.queries.list_groups_query import GroupSummary


class GroupQueryRepository:
    def get(self, group_id: UUID) -> GroupSummary | None:
        entity = Group.objects.all().filter(id=group_id).first()

        return self._summary(entity) if entity is not None else None

    def list(self, *, phase_id: UUID | None = None) -> tuple[GroupSummary, ...]:
        queryset = Group.objects.all()

        if phase_id is not None:
            queryset = queryset.filter(phase_id=phase_id)

        return tuple(self._summary(entity) for entity in queryset)

    @staticmethod
    def _summary(entity: Group) -> GroupSummary:
        from modules.tournaments.application.queries.list_groups_query import GroupSummary

        return GroupSummary(
            id=entity.id,
            phase_id=entity.phase_id,
            name=entity.name,
            tie_break_order=tuple(UUID(value) for value in entity.tie_break_order),
        )
