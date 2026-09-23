from __future__ import annotations

from typing import TYPE_CHECKING

from modules.tournaments.domain.tournament import Tournament

if TYPE_CHECKING:
    from modules.tournaments.application.queries.list_tournaments_query import TournamentSummary


class TournamentQueryRepository:
    def get(self, slug: str) -> TournamentSummary | None:
        entity = Tournament.objects.all().filter(slug=slug).first()

        return self._summary(entity) if entity is not None else None

    def list(self) -> tuple[TournamentSummary, ...]:
        queryset = Tournament.objects.all()

        return tuple(self._summary(entity) for entity in queryset)

    @staticmethod
    def _summary(entity: Tournament) -> TournamentSummary:
        from modules.tournaments.application.queries.list_tournaments_query import TournamentSummary

        return TournamentSummary(
            id=entity.id,
            slug=entity.slug,
            name=entity.name,
            country=entity.country,
            category=entity.category,
            logo=entity.logo.name or None,
            max_teams_per_group=entity.max_teams_per_group,
        )
