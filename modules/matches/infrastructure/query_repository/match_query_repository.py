from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Case, IntegerField, Value, When

from modules.matches.application.queries.team_detail import MatchGoalPreview, TeamDetail
from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal, GoalType
from modules.matches.domain.match import Match, MatchFormation, MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import (
    MatchSquadPlayer,
    MatchSquadRole,
    SentOffReason,
)
from modules.matches.domain.match_substitution import MatchSubstitution
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootout,
    PenaltyShootoutStatus,
)

if TYPE_CHECKING:
    from modules.matches.application.queries.get_match_query import (
        MatchDetail,
        MatchEventDetail,
        MatchSquadPlayerDetail,
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

        rows = tuple(
            matches.order_by("scheduled_at", "id").values(
                "id",
                "status",
                "current_period",
                "current_minute",
                "current_added_minute",
                "scheduled_at",
                "home_team_id",
                "away_team_id",
                "home_team_name",
                "away_team_name",
                "home_goal_count",
                "away_goal_count",
                "penalty_shootout__home_score",
                "penalty_shootout__away_score",
                "home_formation",
                "away_formation",
            )
        )
        goals_by_match = {row["id"]: {TeamSide.HOME: [], TeamSide.AWAY: []} for row in rows}
        for goal in Goal.objects.filter(
            match_id__in=goals_by_match,
            disallowed_at__isnull=True,
        ).order_by("minute", "added_minute", "created_at", "id"):
            goals_by_match[goal.match_id][TeamSide(goal.team_side)].append(
                MatchGoalPreview(
                    player_name=goal.player_name,
                    goal_type=GoalType(goal.goal_type),
                    minute=goal.minute,
                    added_minute=goal.added_minute,
                )
            )

        return tuple(
            MatchSummary(
                id=row["id"],
                status=MatchStatus(row["status"]),
                current_period=(
                    MatchPeriod(row["current_period"])
                    if row["current_period"] is not None
                    else None
                ),
                current_minute=row["current_minute"],
                current_added_minute=row["current_added_minute"],
                scheduled_at=row["scheduled_at"],
                home_team=TeamDetail(
                    id=row["home_team_id"],
                    name=row["home_team_name"],
                    team_side=TeamSide.HOME,
                    score=row["home_goal_count"],
                    penalty_score=row["penalty_shootout__home_score"],
                    formation=(
                        MatchFormation(row["home_formation"])
                        if row["home_formation"] is not None
                        else None
                    ),
                    goals=tuple(goals_by_match[row["id"]][TeamSide.HOME]),
                ),
                away_team=TeamDetail(
                    id=row["away_team_id"],
                    name=row["away_team_name"],
                    team_side=TeamSide.AWAY,
                    score=row["away_goal_count"],
                    penalty_score=row["penalty_shootout__away_score"],
                    formation=(
                        MatchFormation(row["away_formation"])
                        if row["away_formation"] is not None
                        else None
                    ),
                    goals=tuple(goals_by_match[row["id"]][TeamSide.AWAY]),
                ),
            )
            for row in rows
        )

    def get(self, match_id: UUID) -> MatchDetail | None:
        from modules.matches.application.queries.get_match_query import (
            MatchDetail,
            MatchTeamDetail,
        )

        match = (
            Match.objects.filter(id=match_id)
            .values(
                "id",
                "status",
                "current_period",
                "current_minute",
                "current_added_minute",
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
        penalty_shootout = self._get_penalty_shootout(match_id)
        home_lineup = tuple(player for player in lineup if player.team_side == TeamSide.HOME)
        away_lineup = tuple(player for player in lineup if player.team_side == TeamSide.AWAY)
        return MatchDetail(
            id=match["id"],
            status=MatchStatus(match["status"]),
            current_period=(
                MatchPeriod(match["current_period"])
                if match["current_period"] is not None
                else None
            ),
            current_minute=match["current_minute"],
            current_added_minute=match["current_added_minute"],
            scheduled_at=match["scheduled_at"],
            started_at=match["started_at"],
            finished_at=match["finished_at"],
            stadium_name=match["stadium_name"],
            referee_name=match["referee_name"],
            home_team=MatchTeamDetail(
                id=match["home_team_id"],
                name=match["home_team_name"],
                team_side=TeamSide.HOME,
                goals=match["home_goal_count"],
                penalty_score=(penalty_shootout.home_score if penalty_shootout else None),
                formation=(
                    MatchFormation(match["home_formation"])
                    if match["home_formation"] is not None
                    else None
                ),
                lineup=home_lineup,
            ),
            away_team=MatchTeamDetail(
                id=match["away_team_id"],
                name=match["away_team_name"],
                team_side=TeamSide.AWAY,
                goals=match["away_goal_count"],
                penalty_score=(penalty_shootout.away_score if penalty_shootout else None),
                formation=(
                    MatchFormation(match["away_formation"])
                    if match["away_formation"] is not None
                    else None
                ),
                lineup=away_lineup,
            ),
            events=events,
            penalty_shootout=penalty_shootout,
        )

    @staticmethod
    def _get_penalty_shootout(match_id: UUID):
        from modules.matches.application.queries.get_match_query import (
            PenaltyShootoutDetail,
            PenaltyShootoutKickDetail,
        )

        shootout = PenaltyShootout.objects.filter(match_id=match_id).first()

        if shootout is None:
            return None

        kicks = tuple(
            PenaltyShootoutKickDetail(
                id=kick.id,
                player_id=kick.player_id,
                player_name=kick.player_name,
                team_side=TeamSide(kick.team_side),
                sequence_number=kick.sequence_number,
                outcome=PenaltyKickOutcome(kick.outcome),
            )
            for kick in shootout.kicks.order_by("sequence_number")
        )

        return PenaltyShootoutDetail(
            status=PenaltyShootoutStatus(shootout.status),
            home_score=shootout.home_score,
            away_score=shootout.away_score,
            winner_team_side=(
                TeamSide(shootout.winner_team_side)
                if shootout.winner_team_side is not None
                else None
            ),
            kicks=kicks,
        )

    def _get_lineup(self, match_id: UUID) -> tuple[MatchSquadPlayerDetail, ...]:
        from modules.matches.application.queries.get_match_query import (
            MatchSquadPlayerDetail,
        )

        rows = (
            MatchSquadPlayer.objects.filter(match_id=match_id)
            .annotate(
                team_order=Case(
                    When(team_side=TeamSide.HOME, then=Value(0)),
                    When(team_side=TeamSide.AWAY, then=Value(1)),
                    output_field=IntegerField(),
                )
            )
            .order_by("team_order", "shirt_number", "player_id")
            .values(
                "player_id",
                "player__name",
                "team_side",
                "shirt_number",
                "role",
                "is_on_field",
                "is_sent_off",
                "sent_off_reason",
                "is_captain",
            )
        )
        return tuple(
            MatchSquadPlayerDetail(
                player_id=row["player_id"],
                player_name=row["player__name"],
                team_side=TeamSide(row["team_side"]),
                shirt_number=row["shirt_number"],
                role=MatchSquadRole(row["role"]),
                is_on_field=row["is_on_field"],
                is_sent_off=row["is_sent_off"],
                sent_off_reason=(
                    SentOffReason(row["sent_off_reason"])
                    if row["sent_off_reason"] is not None
                    else None
                ),
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
            "id",
            "team_side",
            "player_id",
            "player_name",
            "goal_type",
            "period",
            "minute",
            "added_minute",
            "created_at",
        ):
            events_with_order.append(
                (
                    self._period_order(goal["period"]),
                    goal["minute"],
                    goal["added_minute"],
                    goal["created_at"],
                    MatchEventDetail(
                        id=goal["id"],
                        type=MatchEventType.GOAL,
                        team_side=TeamSide(goal["team_side"]),
                        player_id=goal["player_id"],
                        player_name=goal["player_name"],
                        goal_type=GoalType(goal["goal_type"]),
                        period=MatchPeriod(goal["period"]),
                        minute=goal["minute"],
                        added_minute=goal["added_minute"],
                    ),
                )
            )
        for card in Card.objects.filter(match_id=match_id, rescinded_at__isnull=True).values(
            "id",
            "team_side",
            "player_id",
            "player_name",
            "card_type",
            "period",
            "minute",
            "added_minute",
            "created_at",
        ):
            event_type = (
                MatchEventType.YELLOW_CARD
                if card["card_type"] == CardType.YELLOW
                else MatchEventType.RED_CARD
            )
            events_with_order.append(
                (
                    self._period_order(card["period"]),
                    card["minute"],
                    card["added_minute"],
                    card["created_at"],
                    MatchEventDetail(
                        id=card["id"],
                        type=event_type,
                        team_side=TeamSide(card["team_side"]),
                        player_id=card["player_id"],
                        player_name=card["player_name"],
                        period=MatchPeriod(card["period"]),
                        minute=card["minute"],
                        added_minute=card["added_minute"],
                    ),
                )
            )
        for substitution in MatchSubstitution.objects.filter(match_id=match_id).values(
            "id",
            "team_side",
            "player_out__player_id",
            "player_out__player__name",
            "player_in__player_id",
            "player_in__player__name",
            "period",
            "minute",
            "added_minute",
            "created_at",
        ):
            events_with_order.append(
                (
                    self._period_order(substitution["period"]),
                    substitution["minute"],
                    substitution["added_minute"],
                    substitution["created_at"],
                    MatchEventDetail(
                        id=substitution["id"],
                        type=MatchEventType.SUBSTITUTION,
                        team_side=TeamSide(substitution["team_side"]),
                        period=MatchPeriod(substitution["period"]),
                        minute=substitution["minute"],
                        added_minute=substitution["added_minute"],
                        player_out_id=substitution["player_out__player_id"],
                        player_out_name=substitution["player_out__player__name"],
                        player_in_id=substitution["player_in__player_id"],
                        player_in_name=substitution["player_in__player__name"],
                    ),
                )
            )
        events_with_order.sort(
            key=lambda event: (event[0], event[1], event[2], event[3], event[4].id)
        )
        return tuple(event[4] for event in events_with_order)

    @staticmethod
    def _period_order(period: str) -> int:
        return {
            MatchPeriod.FIRST_HALF: 0,
            MatchPeriod.SECOND_HALF: 1,
            MatchPeriod.EXTRA_TIME_FIRST_HALF: 2,
            MatchPeriod.EXTRA_TIME_SECOND_HALF: 3,
        }[period]
