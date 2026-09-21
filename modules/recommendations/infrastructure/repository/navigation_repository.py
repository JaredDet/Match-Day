from datetime import timedelta

from django.db.models import Count, F, Max, Q

from modules.recommendations.constants import HISTORY_RETENTION_DAYS
from modules.recommendations.domain.navigation_activity import NavigationActivity
from modules.recommendations.domain.navigation_policy import NavigationCounts
from modules.recommendations.domain.visitor import Visitor


class NavigationRepository:
    def get_or_create_visitor(self, visitor_id, now):
        Visitor.objects.get_or_create(
            id=visitor_id, defaults={"created_at": now, "last_seen_at": now, "next_refresh_at": now}
        )
        return self.lock_visitor(visitor_id)

    def lock_visitor(self, visitor_id):
        return Visitor.objects.select_for_update().filter(id=visitor_id).first()

    def save_visitor(self, visitor):
        visitor.save()

    def activity(self, visitor_id, navigation_id):
        return NavigationActivity.objects.filter(
            visitor_id=visitor_id, navigation_id=navigation_id
        ).first()

    def visit_counts(self, visitor_id, reference, now) -> NavigationCounts:
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily = Q(occurred_at__gte=day_start)
        counted_content = Q(
            content_kind=reference.kind, content_id=reference.id, counts_as_visit=True
        )
        counts = NavigationActivity.objects.filter(visitor_id=visitor_id).aggregate(
            daily_total=Count("id", filter=daily),
            daily_content_visits=Count("id", filter=daily & counted_content),
            last_counted_at=Max("occurred_at", filter=counted_content),
        )
        return NavigationCounts(**counts)

    def save_activity(self, activity):
        activity.save()

    def recent_activities(self, visitor_id, now):
        return tuple(
            NavigationActivity.objects.filter(
                visitor_id=visitor_id, occurred_at__gte=now - timedelta(days=HISTORY_RETENTION_DAYS)
            ).order_by("-occurred_at", "id")
        )

    def due_visitors(self, now, limit):
        return tuple(
            Visitor.objects.filter(
                Q(activity_version__gt=F("processed_version")) | Q(next_refresh_at__lte=now)
            )
            .order_by("next_refresh_at", "id")
            .values_list("id", flat=True)[:limit]
        )

    def delete_visitor(self, visitor):
        visitor.delete()

    def purge(self, now):
        cutoff = now - timedelta(days=HISTORY_RETENTION_DAYS)
        activities, _ = NavigationActivity.objects.filter(occurred_at__lt=cutoff).delete()
        visitors, _ = Visitor.objects.filter(last_seen_at__lt=cutoff).delete()
        return {"deleted_activities": activities, "deleted_records": visitors}
