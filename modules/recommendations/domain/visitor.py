import uuid

from django.db import models
from django.utils import timezone


class Visitor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    last_seen_at = models.DateTimeField(default=timezone.now, db_index=True)
    activity_version = models.PositiveBigIntegerField(default=0)
    processed_version = models.PositiveBigIntegerField(default=0)
    next_refresh_at = models.DateTimeField(default=timezone.now, db_index=True)

    def register_activity(self, now) -> None:
        self.last_seen_at = now
        self.activity_version += 1

    def mark_processed(self, next_refresh_at) -> None:
        self.processed_version = self.activity_version
        self.next_refresh_at = next_refresh_at

    class Meta:
        db_table = "recommendation_visitors"
