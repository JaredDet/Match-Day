from __future__ import annotations

import uuid
from datetime import UTC, datetime
from hashlib import sha256
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from core.constants import NAME_MAX_LENGTH
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
    from modules.matches.domain.goal import Goal
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
    status = models.CharField(
        max_length=20,
        choices=MatchStatus.choices,
        default=MatchStatus.SCHEDULED,
    )
    current_period = models.CharField(
        max_length=20,
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
        raise MatchErrors.InvalidPeriod

    def finish(self, finished_at: datetime | None = None) -> None:
        if self.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState
        self._ensure_period(MatchPeriod.SECOND_HALF)
        resolved_finished_at = finished_at or timezone.now()
        if self.started_at is None or resolved_finished_at < self.started_at:
            raise MatchErrors.InvalidFinishTime
        self.status = MatchStatus.FINISHED
        if self.current_minute < 90:
            self.current_minute = 90
            self.current_added_minute = 0
        self.finished_at = resolved_finished_at

    def register_goal(
        self,
        *,
        player: Player,
        minute: int,
        added_minute: int = 0,
        event_id: uuid.UUID | None = None,
    ):
        from modules.matches.domain.goal import Goal

        self._ensure_live()
        period = self._current_event_period()
        team_side = self._resolve_team_side(player.team_id)
        validate_match_event(team_side, period, minute, added_minute)
        self.ensure_event_time_reached(period, minute, added_minute)
        if team_side == TeamSide.HOME:
            self.home_goal_count += 1
        else:
            self.away_goal_count += 1
        return Goal(
            id=event_id or uuid.uuid4(),
            match=self,
            player=player,
            team_side=team_side,
            player_name=player.name,
            period=period,
            minute=minute,
            added_minute=added_minute,
        )

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
        self._ensure_live()
        goal.disallow()
        if goal.team_side == TeamSide.HOME:
            self.home_goal_count -= 1
        else:
            self.away_goal_count -= 1

    def rescind_card(self, card: Card) -> None:
        self._ensure_live()
        card.rescind()
        if card.team_side == TeamSide.HOME:
            self.home_card_count -= 1
        else:
            self.away_card_count -= 1

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
        if period == MatchPeriod.HALFTIME:
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
                        current_minute__lte=90,
                    )
                ),
                name="valid_match_clock_period",
            ),
            models.CheckConstraint(
                condition=models.Q(current_added_minute=0)
                | models.Q(current_minute__in=[45, 90]),
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
                        current_period=MatchPeriod.SECOND_HALF,
                        current_minute=90,
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
