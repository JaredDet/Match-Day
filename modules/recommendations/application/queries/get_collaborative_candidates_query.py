from collections import defaultdict

from injector import inject

from modules.recommendations.constants import COLLABORATIVE_MIN_SHARED_CONTENT
from modules.recommendations.domain.collaborative_policy import CollaborativePolicy
from modules.recommendations.domain.content_reference import ContentReference
from modules.recommendations.domain.recommendation_policy import RecommendationPolicy
from modules.recommendations.infrastructure.query_repository.content_query_repository import (
    ContentQueryRepository,
)
from modules.recommendations.infrastructure.query_repository.similar_visitors_query_repository import (
    SimilarVisitorsQueryRepository,
)


class GetCollaborativeCandidatesQuery:
    @inject
    def __init__(
        self,
        similar_visitors_query_repository: SimilarVisitorsQueryRepository,
        content_query_repository: ContentQueryRepository,
    ):
        self.similar_visitors_query_repository = similar_visitors_query_repository
        self.content_query_repository = content_query_repository

    def execute(self, *, visitor_id, activities, now):
        target = RecommendationPolicy.content_weights(activities, now)
        if (
            len([value for value in target.values() if value > 0])
            < COLLABORATIVE_MIN_SHARED_CONTENT
        ):
            return {}, ()
        peers = self.similar_visitors_query_repository.recent_activities(visitor_id, now)
        contents = self.content_query_repository.resolve(
            {
                ContentReference(activity.content_kind, activity.content_id)
                for activity in (*activities, *peers)
            }
        )
        target = {key: value for key, value in target.items() if key in contents}
        grouped = defaultdict(list)
        for activity in peers:
            grouped[str(activity.visitor_id)].append(activity)
        vectors = {
            visitor: {
                key: value
                for key, value in RecommendationPolicy.content_weights(rows, now).items()
                if key in contents
            }
            for visitor, rows in grouped.items()
        }
        bonuses = CollaborativePolicy.recommend(target, vectors)
        return bonuses, tuple(contents[key] for key in bonuses)
