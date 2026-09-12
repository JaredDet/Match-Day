import uuid

from django.db import models

from core.constants import NAME_MAX_LENGTH
from modules.matches.domain.match_event import (
    MatchPeriod,
    TeamSide,
    timed_match_event_constraints,
)


class ShotOutcome(models.TextChoices):
    OFF_TARGET = "off_target"
    SAVED = "saved"
    BLOCKED = "blocked"
    WOODWORK = "woodwork"


class Shot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="shots",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="shots",
    )
    goalkeeper = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="saved_shots",
        null=True,
        blank=True,
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    player_name = models.CharField(max_length=NAME_MAX_LENGTH)
    goalkeeper_name = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    outcome = models.CharField(max_length=15, choices=ShotOutcome.choices)
    period = models.CharField(max_length=25, choices=MatchPeriod.choices)
    minute = models.PositiveSmallIntegerField()
    added_minute = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "match_shots"
        ordering = ["minute", "added_minute", "created_at"]
        constraints = [
            *timed_match_event_constraints("shot"),
            models.CheckConstraint(
                condition=models.Q(outcome__in=ShotOutcome.values),
                name="valid_shot_outcome",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        outcome=ShotOutcome.SAVED,
                        goalkeeper__isnull=False,
                        goalkeeper_name__isnull=False,
                    )
                    | ~models.Q(outcome=ShotOutcome.SAVED)
                    & models.Q(
                        goalkeeper__isnull=True,
                        goalkeeper_name__isnull=True,
                    )
                ),
                name="valid_shot_goalkeeper",
            ),
        ]
