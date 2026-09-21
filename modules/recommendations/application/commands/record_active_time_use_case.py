from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.recommendations.constants import HISTORY_RETENTION_DAYS
from modules.recommendations.errors import RecommendationErrors
from modules.recommendations.infrastructure.repository.navigation_repository import (
    NavigationRepository,
)


class RecordActiveTimeUseCase:
    @inject
    def __init__(self, navigation_repository: NavigationRepository):
        self.navigation_repository = navigation_repository

    @transaction.atomic
    def execute(
        self, *, visitor_id, navigation_id, content_kind, content_id, active_seconds, now=None
    ):
        now = now or timezone.now()
        visitor = self.navigation_repository.lock_visitor(visitor_id)
        activity = (
            self.navigation_repository.activity(visitor_id, navigation_id) if visitor else None
        )
        if activity is None or activity.occurred_at < now - timedelta(days=HISTORY_RETENTION_DAYS):
            raise RecommendationErrors.ActivityNotFound
        activity.ensure_content(content_kind, content_id)
        if not activity.accumulate_active_time(active_seconds, now):
            return
        self.navigation_repository.save_activity(activity)
        visitor.register_activity(now)
        self.navigation_repository.save_visitor(visitor)
