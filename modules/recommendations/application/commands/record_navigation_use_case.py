from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.recommendations.domain.navigation_activity import NavigationActivity
from modules.recommendations.domain.navigation_policy import NavigationPolicy
from modules.recommendations.infrastructure.query_repository.content_query_repository import (
    ContentQueryRepository,
)
from modules.recommendations.infrastructure.repository.navigation_repository import (
    NavigationRepository,
)


class RecordNavigationUseCase:
    @inject
    def __init__(
        self,
        navigation_repository: NavigationRepository,
        content_query_repository: ContentQueryRepository,
    ):
        self.navigation_repository = navigation_repository
        self.content_query_repository = content_query_repository

    @transaction.atomic
    def execute(self, *, visitor_id, navigation_id, reference, now=None):
        now = now or timezone.now()
        if not self.content_query_repository.exists(reference):
            return None
        visitor = self.navigation_repository.get_or_create_visitor(visitor_id or uuid4(), now)
        if self.navigation_repository.activity(visitor.id, navigation_id):
            return visitor.id
        counts = self.navigation_repository.visit_counts(visitor.id, reference, now)
        if not NavigationPolicy.can_record(counts):
            return visitor.id
        activity = NavigationActivity(
            visitor_id=visitor.id,
            navigation_id=navigation_id,
            content_kind=reference.kind,
            content_id=reference.id,
            occurred_at=now,
            counts_as_visit=NavigationPolicy.counts_as_visit(counts, now),
        )
        self.navigation_repository.save_activity(activity)
        visitor.register_activity(now)
        self.navigation_repository.save_visitor(visitor)
        return visitor.id
