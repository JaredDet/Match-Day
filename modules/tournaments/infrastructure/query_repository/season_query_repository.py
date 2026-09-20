from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from modules.tournaments.domain.season import Season

if TYPE_CHECKING:
    from modules.tournaments.application.queries.list_seasons_query import SeasonSummary


class SeasonQueryRepository:
    def get(self, season_id: UUID) -> SeasonSummary | None:
        entity = Season.objects.all().prefetch_related("teams").filter(id=season_id).first()

        return self._summary(entity) if entity is not None else None

    def list(self, *, tournament_id: UUID | None = None) -> tuple[SeasonSummary, ...]:
        queryset = Season.objects.all().prefetch_related("teams")

        if tournament_id is not None:
            queryset = queryset.filter(tournament_id=tournament_id)

        return tuple(self._summary(entity) for entity in queryset)

    @staticmethod
    def _summary(entity: Season) -> SeasonSummary:
        from modules.tournaments.application.queries.list_seasons_query import SeasonSummary

        return SeasonSummary(
            id=entity.id,
            tournament_id=entity.tournament_id,
            name=entity.name,
            team_ids=tuple(team.id for team in entity.teams.all()),
        )
