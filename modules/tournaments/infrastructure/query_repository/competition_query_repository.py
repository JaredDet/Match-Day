from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Prefetch

from modules.matches.domain.match import Match, MatchStatus
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.phase import Phase, PhaseKind, PhaseStatus
from modules.tournaments.domain.standings import rank_group

if TYPE_CHECKING:
    from modules.tournaments.application.queries.get_season_bracket_query import (
        CupTie,
        SeasonBracket,
    )
    from modules.tournaments.application.queries.get_season_standings_query import StandingGroup


class CompetitionQueryRepository:
    def standings(self, season_id: UUID) -> tuple[StandingGroup, ...]:
        from modules.tournaments.application.queries.get_season_standings_query import (
            StandingGroup,
            StandingRow,
        )

        result = []
        phases = Phase.objects.filter(season_id=season_id, kind=PhaseKind.GROUPS).prefetch_related(
            "groups__entries",
            Prefetch(
                "groups__fixtures",
                queryset=Fixture.objects.filter(match__status=MatchStatus.FINISHED).select_related(
                    "match"
                ),
            ),
        )

        for phase in phases:
            for group in phase.groups.all():
                ordered = rank_group(
                    [entry.team_id for entry in group.entries.all()],
                    [fixture.match for fixture in group.fixtures.all()],
                    group.tie_break_order,
                )

                result.append(
                    StandingGroup(
                        id=group.id,
                        name=group.name,
                        phase_id=phase.id,
                        status=phase.status,
                        matchdays=phase.matchdays,
                        rows=tuple(
                            StandingRow(
                                id=team_id,
                                **row,
                                played=row["wins"] + row["draws"] + row["losses"],
                                goal_difference=row["goals_for"] - row["goals_against"],
                                points=row["wins"] * 3 + row["draws"],
                                qualified=phase.status == PhaseStatus.FINISHED
                                and index < phase.qualifying_teams
                                and not unresolved,
                                tie_break_required=unresolved,
                            )
                            for index, (team_id, row, unresolved) in enumerate(ordered)
                        ),
                    )
                )

        return tuple(result)

    def bracket(self, season_id: UUID) -> SeasonBracket:
        from modules.tournaments.application.queries.get_season_bracket_query import (
            BracketRound,
            SeasonBracket,
        )

        rounds, third = [], None
        phases = Phase.objects.filter(season_id=season_id).exclude(kind=PhaseKind.GROUPS)
        phases = phases.prefetch_related(
            Prefetch("fixtures", queryset=Fixture.objects.select_related("match__penalty_shootout"))
        )

        for phase in phases:
            ties = tuple(self._cup_tie(fixture.match) for fixture in phase.fixtures.all())

            if phase.kind == PhaseKind.THIRD_PLACE:
                third = ties[0] if ties else None
            else:
                rounds.append(BracketRound(id=phase.id, name=phase.name, ties=ties))

        return SeasonBracket(rounds=tuple(rounds), third=third)

    @staticmethod
    def _cup_tie(match: Match) -> CupTie:
        from modules.tournaments.application.queries.get_season_bracket_query import CupTie

        scheduled = match.status == MatchStatus.SCHEDULED
        shootout = getattr(match, "penalty_shootout", None)

        return CupTie(
            id=match.id,
            home_id=match.home_team_id,
            away_id=match.away_team_id,
            home_score=None if scheduled else match.home_goal_count,
            away_score=None if scheduled else match.away_goal_count,
            penalties=(shootout.home_score, shootout.away_score) if shootout else None,
        )
