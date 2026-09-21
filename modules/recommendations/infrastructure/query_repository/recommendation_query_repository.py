from datetime import datetime
from uuid import UUID

from modules.recommendations.application.queries.recommendation_dtos import (
    RecommendationSnapshotDetail,
)
from modules.recommendations.domain.recommendation_snapshot import RecommendationSnapshot


class RecommendationQueryRepository:
    def get_snapshot(
        self, visitor_id: UUID | None, now: datetime
    ) -> RecommendationSnapshotDetail | None:
        row = (
            RecommendationSnapshot.objects.filter(
                key=str(visitor_id) if visitor_id else "general", expires_at__gt=now
            )
            .values("sections", "generated_at", "expires_at")
            .first()
        )
        return RecommendationSnapshotDetail(**row) if row else None
