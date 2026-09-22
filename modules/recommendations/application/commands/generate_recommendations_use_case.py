from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.recommendations.application.queries.get_collaborative_candidates_query import (
    GetCollaborativeCandidatesQuery,
)
from modules.recommendations.constants import SNAPSHOT_MAX_AGE_MINUTES, SNAPSHOT_REFRESH_MINUTES
from modules.recommendations.domain.content_reference import ContentReference
from modules.recommendations.domain.recommendation_policy import (
    InterestWeights,
    RecommendationPolicy,
)
from modules.recommendations.infrastructure.query_repository.content_query_repository import (
    ContentQueryRepository,
)
from modules.recommendations.infrastructure.repository.navigation_repository import (
    NavigationRepository,
)
from modules.recommendations.infrastructure.repository.recommendation_repository import (
    RecommendationRepository,
)


class GenerateRecommendationsUseCase:
    @inject
    def __init__(
        self,
        navigation_repository: NavigationRepository,
        recommendation_repository: RecommendationRepository,
        content_query_repository: ContentQueryRepository,
        collaborative_candidates_query: GetCollaborativeCandidatesQuery,
    ):
        self.navigation_repository = navigation_repository
        self.recommendation_repository = recommendation_repository
        self.content_query_repository = content_query_repository
        self.collaborative_candidates_query = collaborative_candidates_query

    @transaction.atomic
    def execute(self, *, visitor_id=None, now=None):
        now = now or timezone.now()
        profile = InterestWeights({}, {}, frozenset())
        visitor = None
        bonuses, collaborative_contents = {}, ()
        if visitor_id is not None:
            visitor = self.navigation_repository.lock_visitor(visitor_id)
            if visitor is None:
                return False
            activities = self.navigation_repository.recent_activities(visitor_id, now)
            contents = self.content_query_repository.resolve(
                {
                    ContentReference(activity.content_kind, activity.content_id)
                    for activity in activities
                }
            )
            profile = RecommendationPolicy.profile(activities, contents, now)
            self.recommendation_repository.save_profile(visitor_id, profile, now)
            bonuses, collaborative_contents = self.collaborative_candidates_query.execute(
                visitor_id=visitor_id, activities=activities, now=now
            )
        contents = self.content_query_repository.candidates(profile, now)
        contents = {item.reference.key: item for item in (*contents, *collaborative_contents)}
        sections = RecommendationPolicy.recommend(contents.values(), profile, now, bonuses)
        self.recommendation_repository.save_snapshot(
            visitor_id, sections, now, now + timedelta(minutes=SNAPSHOT_MAX_AGE_MINUTES)
        )
        if visitor is not None:
            visitor.mark_processed(now + timedelta(minutes=SNAPSHOT_REFRESH_MINUTES))
            self.navigation_repository.save_visitor(visitor)
        return True
