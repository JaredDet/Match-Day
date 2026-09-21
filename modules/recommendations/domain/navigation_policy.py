from dataclasses import dataclass
from datetime import datetime, timedelta

from modules.recommendations.constants import (
    MAX_CONTENT_VISITS_PER_DAY,
    MAX_VISITOR_VISITS_PER_DAY,
    VISIT_COOLDOWN_MINUTES,
)


@dataclass(frozen=True, slots=True)
class NavigationCounts:
    daily_total: int
    daily_content_visits: int
    last_counted_at: datetime | None


class NavigationPolicy:
    @staticmethod
    def can_record(counts: NavigationCounts) -> bool:
        return counts.daily_total < MAX_VISITOR_VISITS_PER_DAY

    @staticmethod
    def counts_as_visit(counts: NavigationCounts, now: datetime) -> bool:
        if counts.last_counted_at is not None and counts.last_counted_at >= now - timedelta(
            minutes=VISIT_COOLDOWN_MINUTES
        ):
            return False
        return counts.daily_content_visits < MAX_CONTENT_VISITS_PER_DAY
