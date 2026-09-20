from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from modules.tournaments.domain.phase import Phase

if TYPE_CHECKING:
    from modules.tournaments.application.queries.list_phases_query import PhaseSummary


class PhaseQueryRepository:
    def get(self, phase_id: UUID) -> PhaseSummary | None:
        entity = Phase.objects.all().filter(id=phase_id).first()

        return self._summary(entity) if entity is not None else None

    def list(self, *, season_id: UUID | None = None) -> tuple[PhaseSummary, ...]:
        queryset = Phase.objects.all()

        if season_id is not None:
            queryset = queryset.filter(season_id=season_id)

        return tuple(self._summary(entity) for entity in queryset)

    @staticmethod
    def _summary(entity: Phase) -> PhaseSummary:
        from modules.tournaments.application.queries.list_phases_query import PhaseSummary

        return PhaseSummary(
            id=entity.id,
            season_id=entity.season_id,
            name=entity.name,
            kind=entity.kind,
            order=entity.order,
            status=entity.status,
            qualifying_teams=entity.qualifying_teams,
            matchdays=entity.matchdays,
            generated=entity.generated,
            source_phase_id=entity.source_phase_id,
            scheduled_at=entity.scheduled_at,
            expected_matches=entity.expected_matches,
        )
