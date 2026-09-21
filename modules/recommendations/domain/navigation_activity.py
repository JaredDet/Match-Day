import uuid

from django.db import models
from django.utils import timezone

from modules.recommendations.constants import (
    HEARTBEAT_CLOCK_TOLERANCE_SECONDS,
    MAX_ACTIVE_SECONDS_PER_VISIT,
)
from modules.recommendations.domain.content_reference import ContentKind
from modules.recommendations.errors import RecommendationErrors


class NavigationActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visitor = models.ForeignKey(
        "recommendations.Visitor", on_delete=models.CASCADE, related_name="activities"
    )
    navigation_id = models.UUIDField()
    content_kind = models.CharField(max_length=20, choices=ContentKind.choices)
    content_id = models.UUIDField()
    occurred_at = models.DateTimeField(default=timezone.now)
    counts_as_visit = models.BooleanField(default=True)
    active_seconds = models.PositiveSmallIntegerField(default=0)

    def ensure_content(self, content_kind, content_id) -> None:
        if self.content_kind != content_kind or self.content_id != content_id:
            raise RecommendationErrors.ActivityContentMismatch

    def accumulate_active_time(self, active_seconds: int, now) -> bool:
        elapsed = (now - self.occurred_at).total_seconds() + HEARTBEAT_CLOCK_TOLERANCE_SECONDS
        if (
            type(active_seconds) is not int
            or not 0 <= active_seconds <= MAX_ACTIVE_SECONDS_PER_VISIT
            or active_seconds > elapsed
        ):
            raise RecommendationErrors.InvalidActiveTime
        if active_seconds <= self.active_seconds:
            return False
        self.active_seconds = active_seconds
        return True

    class Meta:
        db_table = "recommendation_navigation_activities"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(active_seconds__lte=MAX_ACTIVE_SECONDS_PER_VISIT),
                name="navigation_active_seconds_limit",
            ),
            models.UniqueConstraint(
                fields=["visitor", "navigation_id"], name="unique_visitor_navigation"
            ),
            models.CheckConstraint(
                condition=models.Q(content_kind__in=ContentKind.values),
                name="valid_navigation_content_kind",
            ),
        ]
        indexes = [
            models.Index(fields=["visitor", "occurred_at"], name="navigation_visitor_time"),
            models.Index(fields=["occurred_at"], name="navigation_retention"),
        ]
