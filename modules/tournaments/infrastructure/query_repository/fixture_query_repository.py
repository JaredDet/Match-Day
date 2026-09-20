from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from modules.tournaments.domain.fixture import Fixture

if TYPE_CHECKING:
    from modules.tournaments.application.queries.list_fixtures_query import FixtureSummary


class FixtureQueryRepository:
    def get(self, fixture_id: UUID) -> FixtureSummary | None:
        entity = Fixture.objects.all().filter(id=fixture_id).first()

        return self._summary(entity) if entity is not None else None

    def list(self, *, phase_id: UUID | None = None) -> tuple[FixtureSummary, ...]:
        queryset = Fixture.objects.all()

        if phase_id is not None:
            queryset = queryset.filter(phase_id=phase_id)

        return tuple(self._summary(entity) for entity in queryset)

    @staticmethod
    def _summary(entity: Fixture) -> FixtureSummary:
        from modules.tournaments.application.queries.list_fixtures_query import FixtureSummary

        return FixtureSummary(
            id=entity.id,
            phase_id=entity.phase_id,
            group_id=entity.group_id,
            match_id=entity.match_id,
            position=entity.position,
            matchday=entity.matchday,
        )

    def list_for_season(self, season_id: UUID) -> tuple[FixtureSummary, ...]:
        return tuple(
            self._summary(entity) for entity in Fixture.objects.filter(phase__season_id=season_id)
        )
