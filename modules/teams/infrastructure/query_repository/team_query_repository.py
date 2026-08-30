from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q

from modules.matches.domain.match import Match, MatchStatus
from modules.teams.domain.team import Team

if TYPE_CHECKING:
    from uuid import UUID

    from modules.teams.application.queries.get_team_query import TeamDetail
    from modules.teams.application.queries.list_teams_query import TeamSummary


class TeamQueryRepository:
    def get(self, team_id: UUID) -> TeamDetail | None:
        from modules.teams.application.queries.get_team_query import (
            TeamDetail,
            TeamPlayerDetail,
            TeamRecentMatch,
            TeamStatistics,
        )
        from modules.teams.application.queries.list_teams_query import TeamMatchResult

        team = Team.objects.filter(id=team_id).values("id", "name").first()
        if team is None:
            return None

        fields = (
            "id",
            "home_team_id",
            "away_team_id",
            "home_team_name",
            "away_team_name",
            "home_goal_count",
            "away_goal_count",
            "scheduled_at",
        )
        matches = tuple(
            Match.objects.filter(
                Q(home_team_id=team_id) | Q(away_team_id=team_id),
                status=MatchStatus.FINISHED,
            )
            .order_by("-scheduled_at", "-id")
            .values(*fields)
        )

        recent_matches = []
        wins = draws = losses = goals_for_total = goals_against_total = 0
        for match in matches:
            goals_for, goals_against, opponent_name = self._perspective(match, team_id)
            goals_for_total += goals_for
            goals_against_total += goals_against
            if goals_for > goals_against:
                result = TeamMatchResult.WIN
                wins += 1
            elif goals_for < goals_against:
                result = TeamMatchResult.LOSS
                losses += 1
            else:
                result = TeamMatchResult.DRAW
                draws += 1
            if len(recent_matches) < 5:
                recent_matches.append(
                    TeamRecentMatch(
                        match_id=match["id"],
                        opponent_name=opponent_name,
                        scheduled_at=match["scheduled_at"],
                        goals_for=goals_for,
                        goals_against=goals_against,
                        result=result,
                    )
                )

        captain_id = (
            self._latest_lineup(team_id)
            .filter(is_captain=True)
            .values_list("player_id", flat=True)
            .first()
        )
        players = tuple(
            TeamPlayerDetail(
                id=player["id"],
                name=player["name"],
                is_captain=player["id"] == captain_id,
            )
            for player in Team.objects.get(id=team_id)
            .players.order_by("name", "id")
            .values("id", "name")
        )

        return TeamDetail(
            id=team["id"],
            name=team["name"],
            statistics=TeamStatistics(
                matches_played=len(matches),
                wins=wins,
                draws=draws,
                losses=losses,
                goals_for=goals_for_total,
                goals_against=goals_against_total,
            ),
            players=players,
            recent_matches=tuple(recent_matches),
        )

    def list(self, *, search: str | None = None) -> tuple[TeamSummary, ...]:
        from modules.teams.application.queries.list_teams_query import (
            TeamLastMatch,
            TeamMatchResult,
            TeamNextMatch,
            TeamSummary,
        )

        team_rows = tuple(Team.objects.values("id", "name"))
        normalized_search = search.strip().casefold() if search else ""
        if normalized_search:
            team_rows = tuple(
                row for row in team_rows if normalized_search in row["name"].casefold()
            )
        team_rows = tuple(sorted(team_rows, key=lambda row: (row["name"].casefold(), row["id"])))
        if not team_rows:
            return ()

        team_ids = {row["id"] for row in team_rows}
        related = Q(home_team_id__in=team_ids) | Q(away_team_id__in=team_ids)
        fields = (
            "id",
            "home_team_id",
            "away_team_id",
            "home_team_name",
            "away_team_name",
            "home_goal_count",
            "away_goal_count",
            "scheduled_at",
        )
        finished_matches = (
            Match.objects.filter(
                related,
                status=MatchStatus.FINISHED,
            )
            .order_by("-scheduled_at", "-id")
            .values(*fields)
        )
        scheduled_matches = (
            Match.objects.filter(
                related,
                status=MatchStatus.SCHEDULED,
            )
            .order_by("scheduled_at", "id")
            .values(*fields)
        )

        last_by_team = {}
        for match in finished_matches:
            for team_id in (match["home_team_id"], match["away_team_id"]):
                if team_id in team_ids and team_id not in last_by_team:
                    goals_for, goals_against, opponent_name = self._perspective(match, team_id)
                    result = (
                        TeamMatchResult.WIN
                        if goals_for > goals_against
                        else TeamMatchResult.LOSS
                        if goals_for < goals_against
                        else TeamMatchResult.DRAW
                    )
                    last_by_team[team_id] = TeamLastMatch(
                        match_id=match["id"],
                        opponent_name=opponent_name,
                        goals_for=goals_for,
                        goals_against=goals_against,
                        result=result,
                    )

        next_by_team = {}
        for match in scheduled_matches:
            for team_id in (match["home_team_id"], match["away_team_id"]):
                if team_id in team_ids and team_id not in next_by_team:
                    _, _, opponent_name = self._perspective(match, team_id)
                    next_by_team[team_id] = TeamNextMatch(
                        match_id=match["id"],
                        opponent_name=opponent_name,
                        scheduled_at=match["scheduled_at"],
                    )

        return tuple(
            TeamSummary(
                id=row["id"],
                name=row["name"],
                last_match=last_by_team.get(row["id"]),
                next_match=next_by_team.get(row["id"]),
            )
            for row in team_rows
        )

    @staticmethod
    def _perspective(match, team_id):
        if match["home_team_id"] == team_id:
            return (
                match["home_goal_count"],
                match["away_goal_count"],
                match["away_team_name"],
            )
        return (
            match["away_goal_count"],
            match["home_goal_count"],
            match["home_team_name"],
        )

    @staticmethod
    def _latest_lineup(team_id):
        from modules.matches.domain.match_lineup_player import MatchLineupPlayer

        latest_match_id = (
            MatchLineupPlayer.objects.filter(player__team_id=team_id)
            .order_by("-match__scheduled_at", "-match_id")
            .values_list("match_id", flat=True)
            .first()
        )
        if latest_match_id is None:
            return MatchLineupPlayer.objects.none()
        return MatchLineupPlayer.objects.filter(
            match_id=latest_match_id,
            player__team_id=team_id,
        )
