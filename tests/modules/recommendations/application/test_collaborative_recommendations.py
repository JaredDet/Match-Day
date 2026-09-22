from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from core.dependency_injector import injector_instance
from modules.news.domain.news import News, NewsStatus
from modules.recommendations.application.commands.clear_navigation_history_use_case import (
    ClearNavigationHistoryUseCase,
)
from modules.recommendations.application.commands.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from modules.recommendations.application.commands.record_navigation_use_case import (
    RecordNavigationUseCase,
)
from modules.recommendations.application.queries.get_recommendations_query import (
    GetRecommendationsQuery,
)
from modules.recommendations.domain.content_reference import ContentKind, ContentReference
from modules.recommendations.domain.navigation_activity import NavigationActivity
from modules.recommendations.infrastructure.query_repository.similar_visitors_query_repository import (
    SimilarVisitorsQueryRepository,
)
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_worker_uses_other_visitors_and_respects_clear_history_and_publication():
    now = timezone.now()
    teams = [Team.objects.create(name=name) for name in ("A", "B")]
    news = News.objects.create(
        title="Discovered",
        status=NewsStatus.PUBLISHED,
        content={"children": ["Preview"]},
        published_at=now,
    )
    record = injector_instance.get(RecordNavigationUseCase)
    visitors = []
    for index in range(3):
        visitor_id = None
        for team in teams:
            visitor_id = record.execute(
                visitor_id=visitor_id,
                navigation_id=uuid4(),
                reference=ContentReference(ContentKind.TEAM, team.id),
                now=now,
            )
        if index:
            record.execute(
                visitor_id=visitor_id,
                navigation_id=uuid4(),
                reference=ContentReference(ContentKind.NEWS, news.id),
                now=now,
            )
        visitors.append(visitor_id)
    generate = injector_instance.get(GenerateRecommendationsUseCase)
    query = injector_instance.get(GetRecommendationsQuery)
    generate.execute(visitor_id=visitors[0], now=now)
    feed = query.execute(visitor_id=visitors[0], now=now)
    item = next(item for item in feed.news if item.id == news.id)
    assert item.reason == "similar_visitors"
    assert all(str(visitor) not in str(feed) for visitor in visitors)
    injector_instance.get(ClearNavigationHistoryUseCase).execute(visitor_id=visitors[1])
    generate.execute(visitor_id=visitors[0], now=now)
    assert all(
        item.reason != "similar_visitors"
        for item in query.execute(visitor_id=visitors[0], now=now).news
    )
    News.objects.filter(id=news.id).update(status=NewsStatus.DRAFT)
    assert query.execute(visitor_id=visitors[0], now=now).news == ()


def test_peer_read_excludes_self_expired_events_and_caps_each_history():
    now = timezone.now()
    record = injector_instance.get(RecordNavigationUseCase)
    team = Team.objects.create(name="Team")
    ids = [
        record.execute(
            visitor_id=None,
            navigation_id=uuid4(),
            reference=ContentReference(ContentKind.TEAM, team.id),
            now=now,
        )
        for _ in range(2)
    ]
    NavigationActivity.objects.bulk_create(
        [
            NavigationActivity(
                visitor_id=ids[1],
                navigation_id=uuid4(),
                content_kind="team",
                content_id=team.id,
                occurred_at=now - timedelta(seconds=index),
            )
            for index in range(110)
        ]
    )
    NavigationActivity.objects.create(
        visitor_id=ids[1],
        navigation_id=uuid4(),
        content_kind="team",
        content_id=team.id,
        occurred_at=now - timedelta(days=31),
    )
    peers = injector_instance.get(SimilarVisitorsQueryRepository).recent_activities(ids[0], now)
    assert len(peers) == 100
    assert all(activity.visitor_id == ids[1] for activity in peers)
    assert all(activity.occurred_at >= now - timedelta(days=30) for activity in peers)
