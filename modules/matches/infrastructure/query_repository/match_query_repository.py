from uuid import UUID

from modules.matches.application.queries.match_detail import (
    MatchDetail,
    MatchEventDetail,
    MatchEventType,
    TeamDetail,
)
from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal
from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.match_event import TeamSide


class MatchQueryRepository:
    def get(self, match_id: UUID) -> MatchDetail | None:
        match = (
            Match.objects.filter(id=match_id)
            .values(
                "id",
                "status",
                "scheduled_at",
                "started_at",
                "finished_at",
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
        return MatchDetail(
            id=match["id"],
            status=MatchStatus(match["status"]),
            scheduled_at=match["scheduled_at"],
            started_at=match["started_at"],
            finished_at=match["finished_at"],
            home_team=TeamDetail(
                name=match["home_team_name"],
                goals=match["home_goal_count"],
            ),
            away_team=TeamDetail(
                name=match["away_team_name"],
                goals=match["away_goal_count"],
            ),
            events=events,
        )

    def _get_events(self, match_id: UUID) -> tuple[MatchEventDetail, ...]:
        events_with_order = []
        for goal in Goal.objects.filter(match_id=match_id, cancelled_at__isnull=True).values(
            "id", "team_side", "player_name", "minute", "created_at"
        ):
            events_with_order.append(
                (
                    goal["minute"],
                    goal["created_at"],
                    MatchEventDetail(
                        id=goal["id"],
                        type=MatchEventType.GOAL,
                        team_side=TeamSide(goal["team_side"]),
                        player_name=goal["player_name"],
                        minute=goal["minute"],
                    ),
                )
            )
        for card in Card.objects.filter(match_id=match_id, cancelled_at__isnull=True).values(
            "id", "team_side", "player_name", "card_type", "minute", "created_at"
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
                        player_name=card["player_name"],
                        minute=card["minute"],
                    ),
                )
            )
        events_with_order.sort(key=lambda event: (event[0], event[1], event[2].id))
        return tuple(event[2] for event in events_with_order)
