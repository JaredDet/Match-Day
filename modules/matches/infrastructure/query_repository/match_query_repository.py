from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from modules.matches.application.queries.team_detail import TeamDetail
from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal
from modules.matches.domain.match import Match, MatchFormation, MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_lineup_player import MatchLineupPlayer

if TYPE_CHECKING:
    from modules.matches.application.queries.get_match_query import (
        MatchDetail,
        MatchEventDetail,
        MatchLineupPlayerDetail,
    )
    from modules.matches.application.queries.list_matches_query import MatchSummary


class MatchQueryRepository:
    def list(
        self,
        *,
        status: MatchStatus | None = None,
        date: date | None = None,
    ) -> tuple[MatchSummary, ...]:
        from modules.matches.application.queries.list_matches_query import MatchSummary

        matches = Match.objects.all()
        if status is not None:
            matches = matches.filter(status=status)
        if date is not None:
            matches = matches.filter(scheduled_at__date=date)

        rows = matches.order_by("scheduled_at", "id").values(
            "id",
            "status",
            "scheduled_at",
            "home_team_id",
            "away_team_id",
            "home_team_name",
            "away_team_name",
            "home_goal_count",
            "away_goal_count",
            "home_formation",
            "away_formation",
        )
        return tuple(
            MatchSummary(
                id=row["id"],
                status=MatchStatus(row["status"]),
                scheduled_at=row["scheduled_at"],
                home_team=TeamDetail(
                    id=row["home_team_id"],
                    name=row["home_team_name"],
                    goals=row["home_goal_count"],
                    formation=(
                        MatchFormation(row["home_formation"])
                        if row["home_formation"] is not None
                        else None
                    ),
                ),
                away_team=TeamDetail(
                    id=row["away_team_id"],
                    name=row["away_team_name"],
                    goals=row["away_goal_count"],
                    formation=(
                        MatchFormation(row["away_formation"])
                        if row["away_formation"] is not None
                        else None
                    ),
                ),
            )
            for row in rows
        )

    def get(self, match_id: UUID) -> MatchDetail | None:
        from modules.matches.application.queries.get_match_query import MatchDetail

        match = (
            Match.objects.filter(id=match_id)
            .values(
                "id",
                "status",
                "scheduled_at",
                "started_at",
                "finished_at",
                "stadium_name",
                "referee_name",
                "home_formation",
                "away_formation",
                "home_team_id",
                "away_team_id",
                "home_team_name",
                "away_team_name",
                "home_goal_count",
                "away_goal_count",
            )
            .first()
        )
        if match is None:
            return None

        events = self._get_events(match_id)
        lineup = self._get_lineup(match_id)
        return MatchDetail(
            id=match["id"],
            status=MatchStatus(match["status"]),
            scheduled_at=match["scheduled_at"],
            started_at=match["started_at"],
            finished_at=match["finished_at"],
            stadium_name=match["stadium_name"],
            referee_name=match["referee_name"],
            home_team=TeamDetail(
                id=match["home_team_id"],
                name=match["home_team_name"],
                goals=match["home_goal_count"],
                formation=(
                    MatchFormation(match["home_formation"])
                    if match["home_formation"] is not None
                    else None
                ),
            ),
            away_team=TeamDetail(
                id=match["away_team_id"],
                name=match["away_team_name"],
                goals=match["away_goal_count"],
                formation=(
                    MatchFormation(match["away_formation"])
                    if match["away_formation"] is not None
                    else None
                ),
            ),
            lineup=lineup,
            events=events,
        )

    def _get_lineup(self, match_id: UUID) -> tuple[MatchLineupPlayerDetail, ...]:
        from modules.matches.application.queries.get_match_query import (
            MatchLineupPlayerDetail,
        )

        rows = MatchLineupPlayer.objects.filter(match_id=match_id).values(
            "player_id",
            "player__name",
            "team_side",
            "shirt_number",
            "is_captain",
        )
        return tuple(
            MatchLineupPlayerDetail(
                player_id=row["player_id"],
                player_name=row["player__name"],
                team_side=TeamSide(row["team_side"]),
                shirt_number=row["shirt_number"],
                is_captain=row["is_captain"],
            )
            for row in rows
        )

    def _get_events(self, match_id: UUID) -> tuple[MatchEventDetail, ...]:
        from modules.matches.application.queries.get_match_query import (
            MatchEventDetail,
            MatchEventType,
        )

        events_with_order = []
        for goal in Goal.objects.filter(match_id=match_id, disallowed_at__isnull=True).values(
            "id", "team_side", "player_id", "player_name", "minute", "created_at"
        ):
            events_with_order.append(
                (
                    goal["minute"],
                    goal["created_at"],
                    MatchEventDetail(
                        id=goal["id"],
                        type=MatchEventType.GOAL,
                        team_side=TeamSide(goal["team_side"]),
                        player_id=goal["player_id"],
                        player_name=goal["player_name"],
                        minute=goal["minute"],
                    ),
                )
            )
        for card in Card.objects.filter(match_id=match_id, rescinded_at__isnull=True).values(
            "id",
            "team_side",
            "player_id",
            "player_name",
            "card_type",
            "minute",
            "created_at",
        ):
            event_type = (
                MatchEventType.YELLOW_CARD
                if card["card_type"] == CardType.YELLOW
                else MatchEventType.RED_CARD
            )
            events_with_order.append(
                (
                    card["minute"],
                    card["created_at"],
                    MatchEventDetail(
                        id=card["id"],
                        type=event_type,
                        team_side=TeamSide(card["team_side"]),
                        player_id=card["player_id"],
                        player_name=card["player_name"],
                        minute=card["minute"],
                    ),
                )
            )
        events_with_order.sort(key=lambda event: (event[0], event[1], event[2].id))
        return tuple(event[2] for event in events_with_order)
