from datetime import timedelta

from django.db.models import F, Window
from django.db.models.functions import RowNumber

from modules.recommendations.constants import (
    COLLABORATIVE_ACTIVITIES_PER_VISITOR,
    COLLABORATIVE_MAX_VISITORS,
    HISTORY_RETENTION_DAYS,
)
from modules.recommendations.domain.navigation_activity import NavigationActivity
from modules.recommendations.domain.visitor import Visitor


class SimilarVisitorsQueryRepository:
    def recent_activities(self, visitor_id, now):
        cutoff = now - timedelta(days=HISTORY_RETENTION_DAYS)
        peer_ids = list(
            Visitor.objects.exclude(id=visitor_id)
            .filter(last_seen_at__gte=cutoff)
            .order_by("-last_seen_at", "id")
            .values_list("id", flat=True)[:COLLABORATIVE_MAX_VISITORS]
        )
        return tuple(
            NavigationActivity.objects.filter(
                visitor_id__in=peer_ids, occurred_at__gte=cutoff, occurred_at__lte=now
            )
            .annotate(
                position=Window(
                    expression=RowNumber(),
                    partition_by=[F("visitor_id")],
                    order_by=[F("occurred_at").desc(), F("id").asc()],
                )
            )
            .filter(position__lte=COLLABORATIVE_ACTIVITIES_PER_VISITOR)
            .order_by("-occurred_at", "id")
        )
