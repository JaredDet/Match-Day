import uuid

from django.db import models

from modules.matches.domain.match_event import (
    MatchPeriod,
    TeamSide,
    timed_match_event_constraints,
)


class VarReviewReason(models.TextChoices):
    GOAL = "goal"
    PENALTY = "penalty"
    DIRECT_RED_CARD = "direct_red_card"
    MISTAKEN_IDENTITY = "mistaken_identity"


class VarReviewDecision(models.TextChoices):
    CONFIRMED = "confirmed"
    OVERTURNED = "overturned"
    CHANGED = "changed"


class VarReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="var_reviews",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    reason = models.CharField(max_length=20, choices=VarReviewReason.choices)
    decision = models.CharField(max_length=10, choices=VarReviewDecision.choices)
    reviewed_event_id = models.UUIDField(null=True, blank=True)
    period = models.CharField(max_length=25, choices=MatchPeriod.choices)
    minute = models.PositiveSmallIntegerField()
    added_minute = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "match_var_reviews"
        ordering = ["minute", "added_minute", "created_at"]
        constraints = [
            *timed_match_event_constraints("var_review"),
            models.CheckConstraint(
                condition=models.Q(reason__in=VarReviewReason.values),
                name="valid_var_review_reason",
            ),
            models.CheckConstraint(
                condition=models.Q(decision__in=VarReviewDecision.values),
                name="valid_var_review_decision",
            ),
        ]
