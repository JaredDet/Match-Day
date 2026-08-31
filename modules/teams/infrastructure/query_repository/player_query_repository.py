from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Count, Q

from modules.matches.domain.match import MatchStatus
from modules.teams.domain.player import Player

if TYPE_CHECKING:
    from modules.teams.application.queries.get_player_query import PlayerDetail
    from modules.teams.application.queries.list_players_query import PlayerSummary


class PlayerQueryRepository:
    def get(self, player_id: UUID) -> PlayerDetail | None:
        from modules.matches.domain.card import Card, CardType
        from modules.matches.domain.goal import Goal
        from modules.matches.domain.match_lineup_player import MatchLineupPlayer
        from modules.teams.application.queries.get_player_query import (
            PlayerDetail,
            PlayerRecentMatch,
            PlayerStatistics,
            PlayerTeamDetail,
        )
        from modules.teams.application.queries.list_teams_query import TeamMatchResult

        player = (
            Player.objects.select_related("team")
            .annotate(
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
                yellow_cards_count=Count(
                    "cards__id",
                    filter=Q(
                        cards__card_type=CardType.YELLOW,
                        cards__rescinded_at__isnull=True,
                    ),
                    distinct=True,
                ),
                red_cards_count=Count(
                    "cards__id",
                    filter=Q(
                        cards__card_type=CardType.RED,
                        cards__rescinded_at__isnull=True,
                    ),
                    distinct=True,
                ),
            )
            .filter(id=player_id)
            .first()
        )
        if player is None:
            return None

        lineups = tuple(
            MatchLineupPlayer.objects.filter(
                player_id=player_id,
                match__status=MatchStatus.FINISHED,
            )
            .order_by("-match__scheduled_at", "-match_id")
            .values(
                "match_id",
                "team_side",
                "match__scheduled_at",
                "match__home_team_id",
                "match__away_team_id",
                "match__home_team_name",
                "match__away_team_name",
                "match__home_goal_count",
                "match__away_goal_count",
            )[:5]
        )
        match_ids = [lineup["match_id"] for lineup in lineups]
        goals_by_match = dict(
            Goal.objects.filter(
                player_id=player_id,
                match_id__in=match_ids,
                disallowed_at__isnull=True,
            )
            .values("match_id")
            .annotate(total=Count("id"))
            .values_list("match_id", "total")
        )
        cards_by_match = {
            (row["match_id"], row["card_type"]): row["total"]
            for row in Card.objects.filter(
                player_id=player_id,
                match_id__in=match_ids,
                rescinded_at__isnull=True,
            )
            .values("match_id", "card_type")
            .annotate(total=Count("id"))
        }

        recent_matches = []
        for lineup in lineups:
            is_home = lineup["team_side"] == "home"
            goals_for = (
                lineup["match__home_goal_count"] if is_home else lineup["match__away_goal_count"]
            )
            goals_against = (
                lineup["match__away_goal_count"] if is_home else lineup["match__home_goal_count"]
            )
            result = (
                TeamMatchResult.WIN
                if goals_for > goals_against
                else TeamMatchResult.LOSS
                if goals_for < goals_against
                else TeamMatchResult.DRAW
            )
            match_id = lineup["match_id"]
            recent_matches.append(
                PlayerRecentMatch(
                    match_id=match_id,
                    scheduled_at=lineup["match__scheduled_at"],
                    opponent=PlayerTeamDetail(
                        id=(
                            lineup["match__away_team_id"]
                            if is_home
                            else lineup["match__home_team_id"]
                        ),
                        name=(
                            lineup["match__away_team_name"]
                            if is_home
                            else lineup["match__home_team_name"]
                        ),
                    ),
                    result=result,
                    goals=goals_by_match.get(match_id, 0),
                    yellow_cards=cards_by_match.get((match_id, CardType.YELLOW), 0),
                    red_cards=cards_by_match.get((match_id, CardType.RED), 0),
                )
            )

        return PlayerDetail(
            id=player.id,
            name=player.name,
            preferred_position=player.preferred_position,
            preferred_shirt_number=player.preferred_shirt_number,
            team=PlayerTeamDetail(id=player.team_id, name=player.team.name),
            is_captain=player.team.captain_id == player.id,
            statistics=PlayerStatistics(
                appearances=player.appearances_count,
                goals=player.goals_count,
                yellow_cards=player.yellow_cards_count,
                red_cards=player.red_cards_count,
            ),
            recent_matches=tuple(recent_matches),
        )

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
                preferred_position=player.preferred_position,
                preferred_shirt_number=player.preferred_shirt_number,
                team=PlayerTeamSummary(id=player.team_id, name=player.team.name),
                is_captain=player.team.captain_id == player.id,
                appearances=player.appearances_count,
                goals=player.goals_count,
            )
            for player in rows
        )
