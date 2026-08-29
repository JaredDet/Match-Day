import uuid
from datetime import datetime

from django.db import models
from django.utils import timezone

from modules.matches.errors import MatchErrors


class MatchStatus(models.TextChoices):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home_team_name = models.CharField(max_length=200)
    away_team_name = models.CharField(max_length=200)
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
    ) -> "Match":
        home = home_team_name.strip() if home_team_name else ""
        away = away_team_name.strip() if away_team_name else ""
        if not home or not away or home.casefold() == away.casefold():
            raise MatchErrors.InvalidTeams
        return cls(
            home_team_name=home,
            away_team_name=away,
            scheduled_at=scheduled_at,
        )

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
