from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Count, Q

from modules.matches.domain.match import MatchStatus
from modules.teams.domain.player import Player

if TYPE_CHECKING:
    from modules.teams.application.queries.list_players_query import PlayerSummary


class PlayerQueryRepository:
    def list(
        self,
        *,
        search: str | None = None,
        team_id: UUID | None = None,
    ) -> tuple[PlayerSummary, ...]:
        from modules.teams.application.queries.list_players_query import (
            PlayerSummary,
            PlayerTeamSummary,
        )

        players = Player.objects.select_related("team").annotate(
            appearances_count=Count(
                "match_lineups__match_id",
                filter=Q(match_lineups__match__status=MatchStatus.FINISHED),
                distinct=True,
            ),
            goals_count=Count(
                "goals__id",
                filter=Q(goals__disallowed_at__isnull=True),
                distinct=True,
            ),
        )
        if team_id is not None:
            players = players.filter(team_id=team_id)

        normalized_search = search.strip().casefold() if search else ""
        rows = tuple(
            player
            for player in players
            if not normalized_search or normalized_search in player.name.casefold()
        )
        rows = tuple(
            sorted(
                rows,
                key=lambda player: (
                    player.name.casefold(),
                    player.team.name.casefold(),
                    player.id,
                ),
            )
        )
        return tuple(
            PlayerSummary(
                id=player.id,
                name=player.name,
                team=PlayerTeamSummary(id=player.team_id, name=player.team.name),
                is_captain=player.team.captain_id == player.id,
                appearances=player.appearances_count,
                goals=player.goals_count,
            )
            for player in rows
        )
