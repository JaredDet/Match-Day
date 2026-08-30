from __future__ import annotations

import uuid
from datetime import UTC, datetime
from hashlib import sha256
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from modules.matches.domain.match_event import TeamSide, validate_match_event
from modules.matches.errors import MatchErrors

if TYPE_CHECKING:
    from modules.matches.domain.card import Card, CardType
    from modules.matches.domain.goal import Goal


class MatchStatus(models.TextChoices):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home_team_name = models.CharField(max_length=200)
    away_team_name = models.CharField(max_length=200)
    fixture_key = models.CharField(max_length=64, unique=True, editable=False)
    home_goal_count = models.PositiveSmallIntegerField(default=0)
    away_goal_count = models.PositiveSmallIntegerField(default=0)
    home_card_count = models.PositiveSmallIntegerField(default=0)
    away_card_count = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=MatchStatus.choices,
        default=MatchStatus.SCHEDULED,
    )
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def schedule(
        cls,
        *,
        home_team_name: str,
        away_team_name: str,
        scheduled_at: datetime,
    ) -> Match:
        home = home_team_name.strip() if home_team_name else ""
        away = away_team_name.strip() if away_team_name else ""
        if not home or not away or home.casefold() == away.casefold():
            raise MatchErrors.InvalidTeams
        return cls(
            home_team_name=home,
            away_team_name=away,
            fixture_key=cls.build_fixture_key(home, away, scheduled_at),
            scheduled_at=scheduled_at,
        )

    @staticmethod
    def build_fixture_key(
        home_team_name: str,
        away_team_name: str,
        scheduled_at: datetime,
    ) -> str:
        teams = sorted((home_team_name.strip().casefold(), away_team_name.strip().casefold()))
        if timezone.is_naive(scheduled_at):
            scheduled_at = scheduled_at.replace(tzinfo=UTC)
        instant = scheduled_at.astimezone(UTC).isoformat()
        return sha256(f"{teams[0]}\0{teams[1]}\0{instant}".encode()).hexdigest()

    def start(self, started_at: datetime | None = None) -> None:
        if self.status != MatchStatus.SCHEDULED:
            raise MatchErrors.InvalidState
        self.status = MatchStatus.LIVE
        self.started_at = started_at or timezone.now()

    def finish(self, finished_at: datetime | None = None) -> None:
        if self.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState
        resolved_finished_at = finished_at or timezone.now()
        if self.started_at is None or resolved_finished_at < self.started_at:
            raise MatchErrors.InvalidFinishTime
        self.status = MatchStatus.FINISHED
        self.finished_at = resolved_finished_at

    def register_goal(
        self,
        *,
        team_side: TeamSide,
        player_name: str,
        minute: int,
        event_id: uuid.UUID | None = None,
    ):
        from modules.matches.domain.goal import Goal

        self._ensure_live()
        normalized_player_name = validate_match_event(team_side, player_name, minute)
        if team_side == TeamSide.HOME:
            self.home_goal_count += 1
        else:
            self.away_goal_count += 1
        return Goal(
            id=event_id or uuid.uuid4(),
            match=self,
            team_side=team_side,
            player_name=normalized_player_name,
            minute=minute,
        )

    def register_card(
        self,
        *,
        team_side: TeamSide,
        player_name: str,
        card_type: CardType,
        minute: int,
        event_id: uuid.UUID | None = None,
    ):
        from modules.matches.domain.card import Card, CardType

        self._ensure_live()
        normalized_player_name = validate_match_event(team_side, player_name, minute)
        if not isinstance(card_type, CardType):
            raise MatchErrors.InvalidCardType
        if team_side == TeamSide.HOME:
            self.home_card_count += 1
        else:
            self.away_card_count += 1
        return Card(
            id=event_id or uuid.uuid4(),
            match=self,
            team_side=team_side,
            player_name=normalized_player_name,
            card_type=card_type,
            minute=minute,
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

    class Meta:
        db_table = "matches"
        ordering = ["-scheduled_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=MatchStatus.values),
                name="valid_match_status",
            ),
            models.CheckConstraint(
                condition=~models.Q(home_team_name="") & ~models.Q(away_team_name=""),
                name="match_team_names_not_empty",
            ),
            models.CheckConstraint(
                condition=~models.Q(home_team_name=models.F("away_team_name")),
                name="match_teams_are_different",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status=MatchStatus.SCHEDULED,
                        started_at__isnull=True,
                        finished_at__isnull=True,
                    )
                    | models.Q(
                        status=MatchStatus.LIVE,
                        started_at__isnull=False,
                        finished_at__isnull=True,
                    )
                    | models.Q(
                        status=MatchStatus.FINISHED,
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
