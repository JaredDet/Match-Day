from datetime import datetime
from uuid import UUID

from django.utils import timezone
from injector import inject

from modules.recommendations.application.queries.recommendation_dtos import (
    RecommendationFeed,
    RecommendationItem,
)
from modules.recommendations.domain.content_reference import ContentKind, ContentReference
from modules.recommendations.domain.recommendation_policy import (
    InterestWeights,
    RecommendationPolicy,
)
from modules.recommendations.infrastructure.query_repository.content_query_repository import (
    ContentQueryRepository,
)
from modules.recommendations.infrastructure.query_repository.recommendation_query_repository import (
    RecommendationQueryRepository,
)


class GetRecommendationsQuery:
    @inject
    def __init__(
        self,
        recommendation_query_repository: RecommendationQueryRepository,
        content_query_repository: ContentQueryRepository,
    ):
        self.recommendation_query_repository = recommendation_query_repository
        self.content_query_repository = content_query_repository

    def execute(
        self, *, visitor_id: UUID | None = None, now: datetime | None = None
    ) -> RecommendationFeed:
        now = now or timezone.now()
        snapshot = (
            self.recommendation_query_repository.get_snapshot(visitor_id, now)
            if visitor_id
            else None
        )
        personalized = snapshot is not None
        if snapshot is None:
            snapshot = self.recommendation_query_repository.get_snapshot(None, now)
        if snapshot is None:
            # Cold start: only general content; never calculate the visitor's profile on GET.
            empty_profile = InterestWeights({}, {}, frozenset())
            contents = self.content_query_repository.candidates(empty_profile, now)
            sections = RecommendationPolicy.recommend(contents, empty_profile, now)
        else:
            sections = snapshot.sections
        references = {
            ContentReference(ContentKind(item["kind"]), UUID(item["id"]))
            for items in sections.values()
            for item in items
        }
        current = self.content_query_repository.resolve(references)
        hydrated = {}
        for section, items in sections.items():
            hydrated[section] = []
            for item in items:
                content = current.get(f"{item['kind']}:{item['id']}")
                if content is not None:
                    hydrated[section].append(
                        RecommendationItem(
                            kind=content.reference.kind,
                            id=content.reference.id,
                            title=content.title,
                            endpoint=content.endpoint,
                            preview=content.preview,
                            image=content.image,
                            team_ids=content.team_ids,
                            score=item["score"],
                            reason=item["reason"],
                        )
                    )
        return RecommendationFeed(
            personalized=personalized,
            generated_at=snapshot.generated_at if snapshot else None,
            expires_at=snapshot.expires_at if snapshot else None,
            **{section: tuple(items) for section, items in hydrated.items()},
        )
