from __future__ import annotations

import uuid
from datetime import UTC, datetime
from hashlib import sha256
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from core.constants import NAME_MAX_LENGTH
from modules.matches.constants import (
    EXTRA_TIME_FIRST_HALF_END_MINUTE,
    EXTRA_TIME_FIRST_HALF_START_MINUTE,
    EXTRA_TIME_SECOND_HALF_START_MINUTE,
    MAX_MATCH_MINUTE,
    SECOND_HALF_END_MINUTE,
)
from modules.matches.domain.match_event import (
    MatchPeriod,
    TeamSide,
    validate_match_clock,
    validate_match_event,
)
from modules.matches.domain.match_squad_player import MatchSquadPlayer, MatchSquadRole
from modules.matches.errors import MatchErrors

FIXTURE_KEY_LENGTH = 64

_UNSET = object()

if TYPE_CHECKING:
    from modules.matches.domain.card import Card, CardType
    from modules.matches.domain.corner_kick import CornerKick
    from modules.matches.domain.foul import Foul
    from modules.matches.domain.goal import Goal
    from modules.matches.domain.injury import Injury
    from modules.matches.domain.offside import Offside
    from modules.matches.domain.penalty_attempt import PenaltyAttempt, PenaltyAttemptOutcome
    from modules.matches.domain.shot import Shot, ShotOutcome
    from modules.matches.domain.var_review import VarReview, VarReviewDecision, VarReviewReason
    from modules.teams.domain.player import Player
    from modules.teams.domain.team import Team


class MatchStatus(models.TextChoices):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"


class MatchFormation(models.TextChoices):
    FOUR_THREE_THREE = "4-3-3", "4-3-3"
    FOUR_FOUR_TWO = "4-4-2", "4-4-2"
    FOUR_TWO_THREE_ONE = "4-2-3-1", "4-2-3-1"
    FOUR_ONE_FOUR_ONE = "4-1-4-1", "4-1-4-1"
    THREE_FIVE_TWO = "3-5-2", "3-5-2"
    THREE_FOUR_THREE = "3-4-3", "3-4-3"


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="home_matches",
    )
    away_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="away_matches",
    )
    home_team_name = models.CharField(max_length=NAME_MAX_LENGTH)
    away_team_name = models.CharField(max_length=NAME_MAX_LENGTH)
    home_head_coach_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        null=True,
        blank=True,
    )
    away_head_coach_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        null=True,
        blank=True,
    )
    stadium_name = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    referee_name = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    home_formation = models.CharField(
        max_length=20,
        choices=MatchFormation.choices,
        null=True,
        blank=True,
    )
    away_formation = models.CharField(
        max_length=20,
        choices=MatchFormation.choices,
        null=True,
        blank=True,
    )
    fixture_key = models.CharField(
        max_length=FIXTURE_KEY_LENGTH,
        unique=True,
        editable=False,
    )
    home_goal_count = models.PositiveSmallIntegerField(default=0)
    away_goal_count = models.PositiveSmallIntegerField(default=0)
    home_card_count = models.PositiveSmallIntegerField(default=0)
    away_card_count = models.PositiveSmallIntegerField(default=0)
    home_yellow_card_count = models.PositiveSmallIntegerField(default=0)
    away_yellow_card_count = models.PositiveSmallIntegerField(default=0)
    home_red_card_count = models.PositiveSmallIntegerField(default=0)
    away_red_card_count = models.PositiveSmallIntegerField(default=0)
    home_shot_count = models.PositiveSmallIntegerField(default=0)
    away_shot_count = models.PositiveSmallIntegerField(default=0)
    home_shot_on_target_count = models.PositiveSmallIntegerField(default=0)
    away_shot_on_target_count = models.PositiveSmallIntegerField(default=0)
    home_save_count = models.PositiveSmallIntegerField(default=0)
    away_save_count = models.PositiveSmallIntegerField(default=0)
    home_foul_count = models.PositiveSmallIntegerField(default=0)
    away_foul_count = models.PositiveSmallIntegerField(default=0)
    home_corner_count = models.PositiveSmallIntegerField(default=0)
    away_corner_count = models.PositiveSmallIntegerField(default=0)
    home_offside_count = models.PositiveSmallIntegerField(default=0)
    away_offside_count = models.PositiveSmallIntegerField(default=0)
    home_possession_percentage = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=MatchStatus.choices,
        default=MatchStatus.SCHEDULED,
    )
    current_period = models.CharField(
        max_length=25,
        choices=MatchPeriod.choices,
        null=True,
        blank=True,
    )
    current_minute = models.PositiveSmallIntegerField(null=True, blank=True)
    current_added_minute = models.PositiveSmallIntegerField(default=0)
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def schedule(
        cls,
        *,
        home_team: Team,
        away_team: Team,
        scheduled_at: datetime,
        stadium_name: str | None = None,
        referee_name: str | None = None,
    ) -> Match:
        if home_team.id == away_team.id:
            raise MatchErrors.InvalidTeams
        return cls(
            home_team=home_team,
            away_team=away_team,
            home_team_name=home_team.name,
            away_team_name=away_team.name,
            home_head_coach_name=home_team.head_coach_name,
            away_head_coach_name=away_team.head_coach_name,
            stadium_name=cls._normalize_optional_name(stadium_name),
            referee_name=cls._normalize_optional_name(referee_name),
            fixture_key=cls.build_fixture_key(home_team.id, away_team.id, scheduled_at),
            scheduled_at=scheduled_at,
        )

    def update_details(
        self,
        *,
        stadium_name=_UNSET,
        referee_name=_UNSET,
    ) -> None:
        if stadium_name is not _UNSET:
            self.stadium_name = self._normalize_optional_name(stadium_name)
        if referee_name is not _UNSET:
            self.referee_name = self._normalize_optional_name(referee_name)

    def set_formation(
        self,
        *,
        team_side: TeamSide,
        formation: MatchFormation,
    ) -> None:
        if self.status != MatchStatus.SCHEDULED:
            raise MatchErrors.InvalidState
        if not isinstance(team_side, TeamSide):
            raise MatchErrors.InvalidTeamSide
        if not isinstance(formation, MatchFormation):
            raise MatchErrors.InvalidFormation
        if team_side == TeamSide.HOME:
            self.home_formation = formation
        else:
            self.away_formation = formation

    def add_squad_player(
        self,
        *,
        player: Player,
        shirt_number: int,
        role: MatchSquadRole = MatchSquadRole.STARTER,
        is_captain: bool = False,
    ) -> MatchSquadPlayer:
        team_side = self._resolve_team_side(player.team_id)
        return MatchSquadPlayer.create(
            match=self,
            player=player,
            team_side=team_side,
            shirt_number=shirt_number,
            role=role,
            is_captain=is_captain,
        )

    @staticmethod
    def _normalize_optional_name(value: str | None) -> str | None:
        normalized_value = " ".join(value.split()) if value else ""
        return normalized_value or None

    @staticmethod
    def build_fixture_key(
        home_team_id: uuid.UUID,
        away_team_id: uuid.UUID,
        scheduled_at: datetime,
    ) -> str:
        teams = sorted((str(home_team_id), str(away_team_id)))
        if timezone.is_naive(scheduled_at):
            scheduled_at = scheduled_at.replace(tzinfo=UTC)
        instant = scheduled_at.astimezone(UTC).isoformat()
        return sha256(f"{teams[0]}\0{teams[1]}\0{instant}".encode()).hexdigest()

    def start(self, started_at: datetime | None = None) -> None:
        if self.status != MatchStatus.SCHEDULED:
            raise MatchErrors.InvalidState
        self.status = MatchStatus.LIVE
        self.current_period = MatchPeriod.FIRST_HALF
        self.current_minute = 1
        self.current_added_minute = 0
        self.started_at = started_at or timezone.now()

    def ensure_ready_for_start(self, squad_players: list[MatchSquadPlayer]) -> None:
        if self.status != MatchStatus.SCHEDULED:
            raise MatchErrors.InvalidState
        if self.home_formation is None or self.away_formation is None:
            raise MatchErrors.MissingFormation
        for team_side in TeamSide:
            team_players = [player for player in squad_players if player.team_side == team_side]
            starters = [player for player in team_players if player.role == MatchSquadRole.STARTER]
            substitutes = [
                player for player in team_players if player.role == MatchSquadRole.SUBSTITUTE
            ]
            if (
                len(starters) != 11
                or any(not player.is_on_field for player in starters)
                or any(player.is_on_field for player in substitutes)
                or any(player.is_captain for player in substitutes)
            ):
                raise MatchErrors.InvalidStartingSquad

    def end_first_half(self) -> None:
        self._ensure_period(MatchPeriod.FIRST_HALF)
        if self.current_minute < 45:
            self.current_minute = 45
            self.current_added_minute = 0
        self.current_period = MatchPeriod.HALFTIME

    def start_second_half(self) -> None:
        self._ensure_period(MatchPeriod.HALFTIME)
        self.current_period = MatchPeriod.SECOND_HALF
        self.current_minute = 46
        self.current_added_minute = 0

    def update_clock(
        self,
        *,
        expected_period: MatchPeriod,
        minute: int,
        added_minute: int = 0,
    ) -> None:
        self._ensure_live()
        if self.current_period != expected_period:
            raise MatchErrors.PeriodMismatch
        validate_match_clock(expected_period, minute, added_minute)
        if (minute, added_minute) < (
            self.current_minute,
            self.current_added_minute,
        ):
            raise MatchErrors.ClockCannotGoBackwards
        self.current_minute = minute
        self.current_added_minute = added_minute

    def advance_period(self, expected_period: MatchPeriod) -> None:
        self._ensure_live()
        if self.current_period != expected_period:
            raise MatchErrors.PeriodMismatch
        if expected_period == MatchPeriod.FIRST_HALF:
            self.end_first_half()
            return
        if expected_period == MatchPeriod.HALFTIME:
            self.start_second_half()
            return
        if expected_period == MatchPeriod.SECOND_HALF:
            self.start_extra_time()
            return
        if expected_period == MatchPeriod.EXTRA_TIME_FIRST_HALF:
            self.end_extra_time_first_half()
            return
        if expected_period == MatchPeriod.EXTRA_TIME_HALFTIME:
            self.start_extra_time_second_half()
            return
        raise MatchErrors.InvalidPeriod

    def start_extra_time(self) -> None:
        self._ensure_period(MatchPeriod.SECOND_HALF)

        if self.current_minute != SECOND_HALF_END_MINUTE:
            raise MatchErrors.InvalidExtraTimeState

        if self.home_goal_count != self.away_goal_count:
            raise MatchErrors.ExtraTimeRequiresTie

        self.current_period = MatchPeriod.EXTRA_TIME_FIRST_HALF
        self.current_minute = EXTRA_TIME_FIRST_HALF_START_MINUTE
        self.current_added_minute = 0

    def end_extra_time_first_half(self) -> None:
        self._ensure_period(MatchPeriod.EXTRA_TIME_FIRST_HALF)

        if self.current_minute < EXTRA_TIME_FIRST_HALF_END_MINUTE:
            self.current_minute = EXTRA_TIME_FIRST_HALF_END_MINUTE
            self.current_added_minute = 0

        self.current_period = MatchPeriod.EXTRA_TIME_HALFTIME

    def start_extra_time_second_half(self) -> None:
        self._ensure_period(MatchPeriod.EXTRA_TIME_HALFTIME)
        self.current_period = MatchPeriod.EXTRA_TIME_SECOND_HALF
        self.current_minute = EXTRA_TIME_SECOND_HALF_START_MINUTE
        self.current_added_minute = 0

    def finish(self, finished_at: datetime | None = None) -> None:
        if self.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState
        if self.current_period not in {
            MatchPeriod.SECOND_HALF,
            MatchPeriod.EXTRA_TIME_SECOND_HALF,
        }:
            raise MatchErrors.InvalidPeriod
        resolved_finished_at = finished_at or timezone.now()
        if self.started_at is None or resolved_finished_at < self.started_at:
            raise MatchErrors.InvalidFinishTime
        self.status = MatchStatus.FINISHED
        expected_final_minute = (
            MAX_MATCH_MINUTE
            if self.current_period == MatchPeriod.EXTRA_TIME_SECOND_HALF
            else SECOND_HALF_END_MINUTE
        )
        if self.current_minute < expected_final_minute:
            self.current_minute = expected_final_minute
            self.current_added_minute = 0
        self.finished_at = resolved_finished_at

    def register_goal(
        self,
        *,
        player: Player,
        assist_player: Player | None = None,
        minute: int,
        added_minute: int = 0,
        goal_type=None,
        event_id: uuid.UUID | None = None,
    ):
        from modules.matches.domain.goal import Goal, GoalType

        self._ensure_live()
        period = self._current_event_period()
        team_side = self._resolve_team_side(player.team_id)
        validate_match_event(team_side, period, minute, added_minute)
        self.ensure_event_time_reached(period, minute, added_minute)
        resolved_goal_type = goal_type or GoalType.REGULAR
        if not isinstance(resolved_goal_type, GoalType):
            raise MatchErrors.InvalidGoalType

        if resolved_goal_type == GoalType.OWN_GOAL:
            team_side = TeamSide.AWAY if team_side == TeamSide.HOME else TeamSide.HOME

        if assist_player is not None and (
            resolved_goal_type != GoalType.REGULAR
            or assist_player.id == player.id
            or assist_player.team_id != player.team_id
        ):
            raise MatchErrors.InvalidGoalAssist

        if team_side == TeamSide.HOME:
            self.home_goal_count += 1
        else:
            self.away_goal_count += 1

        if resolved_goal_type != GoalType.OWN_GOAL:
            self._increment_counter(team_side, "shot")
            self._increment_counter(team_side, "shot_on_target")

        return Goal(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            assist_player=assist_player,
            team_side=team_side,
            player_name=player.name,
            assist_player_name=(assist_player.name if assist_player is not None else None),
            goal_type=resolved_goal_type,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def register_penalty_attempt(
        self,
        *,
        player: Player,
        outcome: PenaltyAttemptOutcome,
        minute: int,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ) -> PenaltyAttempt:
        from modules.matches.domain.penalty_attempt import (
            PenaltyAttempt,
            PenaltyAttemptOutcome,
        )

        self._ensure_live()
        period = self._current_event_period()
        team_side = self._resolve_team_side(player.team_id)
        validate_match_event(team_side, period, minute, added_minute)
        self.ensure_event_time_reached(period, minute, added_minute)

        if not isinstance(outcome, PenaltyAttemptOutcome):
            raise MatchErrors.InvalidPenaltyAttemptOutcome

        self._increment_counter(team_side, "shot")
        if outcome == PenaltyAttemptOutcome.SAVED:
            self._increment_counter(team_side, "shot_on_target")
            self._increment_counter(self._opposite_side(team_side), "save")

        return PenaltyAttempt(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            team_side=team_side,
            player_name=player.name,
            outcome=outcome,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def register_injury(
        self,
        *,
        player: Player,
        minute: int,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ) -> Injury:
        from modules.matches.domain.injury import Injury

        self._ensure_live()
        period = self._current_event_period()
        team_side = self._resolve_team_side(player.team_id)
        validate_match_event(team_side, period, minute, added_minute)
        self.ensure_event_time_reached(period, minute, added_minute)

        return Injury(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            team_side=team_side,
            player_name=player.name,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def register_var_review(
        self,
        *,
        team_side: TeamSide,
        reason: VarReviewReason,
        decision: VarReviewDecision,
        minute: int,
        added_minute: int = 0,
        reviewed_event_id: uuid.UUID | None = None,
        event_id: uuid.UUID | None = None,
    ) -> VarReview:
        from modules.matches.domain.var_review import (
            VarReview,
            VarReviewDecision,
            VarReviewReason,
        )

        self._ensure_live()
        period = self._current_event_period()
        validate_match_event(team_side, period, minute, added_minute)
        self.ensure_event_time_reached(period, minute, added_minute)

        if not isinstance(reason, VarReviewReason):
            raise MatchErrors.InvalidVarReviewReason

        if not isinstance(decision, VarReviewDecision):
            raise MatchErrors.InvalidVarReviewDecision

        return VarReview(
            id=event_id or uuid.uuid4(),
            match=self,
            team_side=team_side,
            reason=reason,
            decision=decision,
            reviewed_event_id=reviewed_event_id,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def register_foul(
        self,
        *,
        player: Player,
        minute: int,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ) -> Foul:
        from modules.matches.domain.foul import Foul

        period, team_side = self._prepare_player_event(player, minute, added_minute)
        self._increment_counter(team_side, "foul")

        return Foul(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            team_side=team_side,
            player_name=player.name,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def register_corner_kick(
        self,
        *,
        player: Player,
        minute: int,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ) -> CornerKick:
        from modules.matches.domain.corner_kick import CornerKick

        period, team_side = self._prepare_player_event(player, minute, added_minute)
        self._increment_counter(team_side, "corner")

        return CornerKick(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            team_side=team_side,
            player_name=player.name,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def register_offside(
        self,
        *,
        player: Player,
        minute: int,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ) -> Offside:
        from modules.matches.domain.offside import Offside

        period, team_side = self._prepare_player_event(player, minute, added_minute)
        self._increment_counter(team_side, "offside")

        return Offside(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            team_side=team_side,
            player_name=player.name,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def register_shot(
        self,
        *,
        player: Player,
        outcome: ShotOutcome,
        minute: int,
        goalkeeper: Player | None = None,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ) -> Shot:
        from modules.matches.domain.shot import Shot, ShotOutcome

        period, team_side = self._prepare_player_event(player, minute, added_minute)

        if not isinstance(outcome, ShotOutcome):
            raise MatchErrors.InvalidShotOutcome
        if (outcome == ShotOutcome.SAVED) != (goalkeeper is not None):
            raise MatchErrors.InvalidShotGoalkeeper
        if goalkeeper is not None:
            goalkeeper_side = self._resolve_team_side(goalkeeper.team_id)
            if goalkeeper_side == team_side:
                raise MatchErrors.InvalidShotGoalkeeper

        self._increment_counter(team_side, "shot")
        if outcome == ShotOutcome.SAVED:
            self._increment_counter(team_side, "shot_on_target")
            self._increment_counter(self._opposite_side(team_side), "save")

        return Shot(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            goalkeeper=goalkeeper,
            team_side=team_side,
            player_name=player.name,
            goalkeeper_name=goalkeeper.name if goalkeeper is not None else None,
            outcome=outcome,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def update_possession(self, home_percentage: int) -> None:
        self._ensure_live()
        if (
            not isinstance(home_percentage, int)
            or isinstance(home_percentage, bool)
            or not 0 <= home_percentage <= 100
        ):
            raise MatchErrors.InvalidPossession

        self.home_possession_percentage = home_percentage

    def ensure_penalty_shootout_can_start(self) -> None:
        self._ensure_live()

        valid_end = (
            self.current_period == MatchPeriod.SECOND_HALF
            and self.current_minute == SECOND_HALF_END_MINUTE
        ) or (
            self.current_period == MatchPeriod.EXTRA_TIME_SECOND_HALF
            and self.current_minute == MAX_MATCH_MINUTE
        )

        if not valid_end:
            raise MatchErrors.InvalidPenaltyShootoutState

        if self.home_goal_count != self.away_goal_count:
            raise MatchErrors.PenaltyShootoutRequiresTie

    def register_card(
        self,
        *,
        player: Player,
        card_type: CardType,
        minute: int,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ):
        from modules.matches.domain.card import Card, CardType

        self._ensure_live()
        period = self._current_event_period()
        team_side = self._resolve_team_side(player.team_id)
        validate_match_event(team_side, period, minute, added_minute)
        self.ensure_event_time_reached(period, minute, added_minute)
        if not isinstance(card_type, CardType):
            raise MatchErrors.InvalidCardType

        if team_side == TeamSide.HOME:
            self.home_card_count += 1
        else:
            self.away_card_count += 1

        counter = "yellow_card" if card_type == CardType.YELLOW else "red_card"
        self._increment_counter(team_side, counter)

        return Card(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            team_side=team_side,
            player_name=player.name,
            card_type=card_type,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

    def disallow_goal(self, goal: Goal) -> None:
        from modules.matches.domain.goal import GoalType

        self._ensure_live()
        goal.disallow()
        if goal.team_side == TeamSide.HOME:
            self.home_goal_count -= 1
        else:
            self.away_goal_count -= 1

        if goal.goal_type != GoalType.OWN_GOAL:
            self._decrement_counter(TeamSide(goal.team_side), "shot")
            self._decrement_counter(TeamSide(goal.team_side), "shot_on_target")

    def rescind_card(self, card: Card) -> None:
        from modules.matches.domain.card import CardType

        self._ensure_live()
        card.rescind()
        if card.team_side == TeamSide.HOME:
            self.home_card_count -= 1
        else:
            self.away_card_count -= 1

        counter = "yellow_card" if card.card_type == CardType.YELLOW else "red_card"
        self._decrement_counter(TeamSide(card.team_side), counter)

    def _ensure_live(self) -> None:
        if self.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState

    def _ensure_period(self, expected_period: MatchPeriod) -> None:
        self._ensure_live()
        if self.current_period != expected_period:
            raise MatchErrors.InvalidPeriod

    def _current_event_period(self) -> MatchPeriod:
        try:
            period = MatchPeriod(self.current_period)
        except (TypeError, ValueError):
            raise MatchErrors.InvalidPeriod from None
        if period in {MatchPeriod.HALFTIME, MatchPeriod.EXTRA_TIME_HALFTIME}:
            raise MatchErrors.InvalidPeriod
        return period

    def ensure_event_time_reached(
        self,
        period: MatchPeriod,
        minute: int,
        added_minute: int,
    ) -> None:
        if period != self.current_period or (minute, added_minute) > (
            self.current_minute,
            self.current_added_minute,
        ):
            raise MatchErrors.EventAheadOfClock

    def _prepare_player_event(
        self,
        player: Player,
        minute: int,
        added_minute: int,
    ) -> tuple[MatchPeriod, TeamSide]:
        self._ensure_live()
        period = self._current_event_period()
        team_side = self._resolve_team_side(player.team_id)
        validate_match_event(team_side, period, minute, added_minute)
        self.ensure_event_time_reached(period, minute, added_minute)
        return period, team_side

    def _increment_counter(self, team_side: TeamSide, counter: str) -> None:
        field = f"{team_side.value}_{counter}_count"
        setattr(self, field, getattr(self, field) + 1)

    def _decrement_counter(self, team_side: TeamSide, counter: str) -> None:
        field = f"{team_side.value}_{counter}_count"
        setattr(self, field, max(0, getattr(self, field) - 1))

    @staticmethod
    def _opposite_side(team_side: TeamSide) -> TeamSide:
        return TeamSide.AWAY if team_side == TeamSide.HOME else TeamSide.HOME

    def _resolve_team_side(self, team_id: uuid.UUID) -> TeamSide:
        if team_id == self.home_team_id:
            return TeamSide.HOME
        if team_id == self.away_team_id:
            return TeamSide.AWAY
        raise MatchErrors.InvalidPlayerTeam

    class Meta:
        db_table = "matches"
        ordering = ["-scheduled_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=MatchStatus.values),
                name="valid_match_status",
            ),
            models.CheckConstraint(
                condition=models.Q(current_period__isnull=True)
                | models.Q(current_period__in=MatchPeriod.values),
                name="valid_match_period",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(current_period__isnull=True, current_minute__isnull=True)
                    | models.Q(
                        current_period=MatchPeriod.FIRST_HALF,
                        current_minute__gte=1,
                        current_minute__lte=45,
                    )
                    | models.Q(
                        current_period=MatchPeriod.HALFTIME,
                        current_minute=45,
                    )
                    | models.Q(
                        current_period=MatchPeriod.SECOND_HALF,
                        current_minute__gte=46,
                        current_minute__lte=SECOND_HALF_END_MINUTE,
                    )
                    | models.Q(
                        current_period=MatchPeriod.EXTRA_TIME_FIRST_HALF,
                        current_minute__gte=EXTRA_TIME_FIRST_HALF_START_MINUTE,
                        current_minute__lte=EXTRA_TIME_FIRST_HALF_END_MINUTE,
                    )
                    | models.Q(
                        current_period=MatchPeriod.EXTRA_TIME_HALFTIME,
                        current_minute=EXTRA_TIME_FIRST_HALF_END_MINUTE,
                    )
                    | models.Q(
                        current_period=MatchPeriod.EXTRA_TIME_SECOND_HALF,
                        current_minute__gte=EXTRA_TIME_SECOND_HALF_START_MINUTE,
                        current_minute__lte=MAX_MATCH_MINUTE,
                    )
                ),
                name="valid_match_clock_period",
            ),
            models.CheckConstraint(
                condition=models.Q(current_added_minute=0)
                | models.Q(
                    current_minute__in=[
                        45,
                        SECOND_HALF_END_MINUTE,
                        EXTRA_TIME_FIRST_HALF_END_MINUTE,
                        MAX_MATCH_MINUTE,
                    ]
                ),
                name="valid_match_clock_added_minute",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(home_formation__isnull=True)
                    | models.Q(home_formation__in=MatchFormation.values)
                ),
                name="valid_home_match_formation",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(away_formation__isnull=True)
                    | models.Q(away_formation__in=MatchFormation.values)
                ),
                name="valid_away_match_formation",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(home_possession_percentage__isnull=True)
                    | models.Q(home_possession_percentage__lte=100)
                ),
                name="valid_home_possession_percentage",
            ),
            models.CheckConstraint(
                condition=~models.Q(home_team=models.F("away_team")),
                name="match_teams_are_different",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status=MatchStatus.SCHEDULED,
                        current_period__isnull=True,
                        current_minute__isnull=True,
                        current_added_minute=0,
                        started_at__isnull=True,
                        finished_at__isnull=True,
                    )
                    | models.Q(
                        status=MatchStatus.LIVE,
                        current_period__in=MatchPeriod.values,
                        current_minute__isnull=False,
                        started_at__isnull=False,
                        finished_at__isnull=True,
                    )
                    | models.Q(
                        status=MatchStatus.FINISHED,
                        current_period__in=[
                            MatchPeriod.SECOND_HALF,
                            MatchPeriod.EXTRA_TIME_SECOND_HALF,
                        ],
                        current_minute__in=[SECOND_HALF_END_MINUTE, MAX_MATCH_MINUTE],
                        started_at__isnull=False,
                        finished_at__isnull=False,
                    )
                ),
                name="valid_match_lifecycle_timestamps",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(finished_at__isnull=True)
                    | models.Q(finished_at__gte=models.F("started_at"))
                ),
                name="match_finish_after_start",
            ),
        ]
