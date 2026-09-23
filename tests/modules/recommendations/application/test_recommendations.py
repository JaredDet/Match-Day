from datetime import timedelta
from io import StringIO
from uuid import uuid4

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.dependency_injector import injector_instance
from modules.news.domain.news import News, NewsStatus
from modules.recommendations.application.commands.clear_navigation_history_use_case import (
    ClearNavigationHistoryUseCase,
)
from modules.recommendations.application.commands.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from modules.recommendations.application.commands.process_recommendations_use_case import (
    ProcessRecommendationsUseCase,
)
from modules.recommendations.application.commands.purge_navigation_history_use_case import (
    PurgeNavigationHistoryUseCase,
)
from modules.recommendations.application.commands.record_active_time_use_case import (
    RecordActiveTimeUseCase,
)
from modules.recommendations.application.commands.record_navigation_use_case import (
    RecordNavigationUseCase,
)
from modules.recommendations.application.queries.get_recommendations_query import (
    GetRecommendationsQuery,
)
from modules.recommendations.domain.content_reference import ContentKind, ContentReference
from modules.recommendations.domain.interest_profile import InterestProfile
from modules.recommendations.domain.navigation_activity import NavigationActivity
from modules.recommendations.domain.recommendation_snapshot import RecommendationSnapshot
from modules.recommendations.domain.visitor import Visitor
from modules.recommendations.infrastructure.query_repository.content_query_repository import (
    ContentQueryRepository,
)
from modules.teams.domain.team import Team
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament

pytestmark = pytest.mark.django_db


def record(team, *, visitor_id=None, now=None):
    navigation_id = uuid4()
    id = injector_instance.get(RecordNavigationUseCase).execute(
        visitor_id=visitor_id,
        navigation_id=navigation_id,
        reference=ContentReference(ContentKind.TEAM, team.id),
        now=now,
    )
    return id, navigation_id


def test_worker_persists_profile_and_snapshot_get_does_not_recalculate():
    team = Team.objects.create(name="Club")
    news = News.objects.create(
        title="Club news",
        team=team,
        content={"children": ["Preview", "Full text"]},
        status=NewsStatus.PUBLISHED,
        published_at=timezone.now(),
    )
    visitor_id, _ = record(team)
    assert not InterestProfile.objects.exists()
    assert injector_instance.get(ProcessRecommendationsUseCase).execute() == 1
    profile = InterestProfile.objects.get(visitor_id=visitor_id)
    assert profile.team_weights[str(team.id)] > 0
    result = injector_instance.get(GetRecommendationsQuery).execute(visitor_id=visitor_id)
    assert result.personalized
    assert result.news[0].id == news.id
    assert result.news[0].preview == "Preview"
    assert not hasattr(result.news[0], "content")
    assert result.news[0].reason == "team_interest"
    assert injector_instance.get(ProcessRecommendationsUseCase).execute() == 0
    profile.refresh_from_db()
    assert result.generated_at == profile.computed_at


def test_expired_snapshot_falls_back_without_recalculating_personal_profile():
    team = Team.objects.create(name="Club")
    id, _ = record(team)
    injector_instance.get(ProcessRecommendationsUseCase).execute()
    snapshot = RecommendationSnapshot.objects.get(visitor_id=id)
    RecommendationSnapshot.objects.filter(visitor_id=id).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )
    result = injector_instance.get(GetRecommendationsQuery).execute(visitor_id=id)
    assert not result.personalized
    assert InterestProfile.objects.get(visitor_id=id).computed_at == snapshot.generated_at


def test_snapshot_rechecks_publication_and_current_titles():
    public = News.objects.create(
        title="Public",
        content={"children": ["Text"]},
        status=NewsStatus.PUBLISHED,
        published_at=timezone.now(),
    )
    draft = News.objects.create(title="Private", content={"children": ["Hidden"]})
    injector_instance.get(GenerateRecommendationsUseCase).execute()
    result = injector_instance.get(GetRecommendationsQuery).execute()
    assert [item.id for item in result.news] == [public.id]
    News.objects.filter(id=public.id).update(status=NewsStatus.DRAFT)
    assert injector_instance.get(GetRecommendationsQuery).execute().news == ()
    assert str(draft.id) not in str(result)


def test_clear_history_removes_profile_snapshot_and_background_cannot_resurrect_it():
    id, _ = record(Team.objects.create(name="Club"))
    injector_instance.get(ProcessRecommendationsUseCase).execute()
    injector_instance.get(ClearNavigationHistoryUseCase).execute(visitor_id=id)
    assert not Visitor.objects.exists()
    assert not NavigationActivity.objects.exists()
    assert not InterestProfile.objects.exists()
    assert not RecommendationSnapshot.objects.filter(visitor_id=id).exists()
    assert not injector_instance.get(GenerateRecommendationsUseCase).execute(visitor_id=id)


def test_delete_history_requires_csrf_and_clears_the_cookie():
    client = APIClient(enforce_csrf_checks=True)
    team = Team.objects.create(name="Club")
    client.get(
        reverse("teams-detail", args=[team.id]),
        HTTP_X_NAVIGATION_INTENT="detail-view",
        HTTP_X_NAVIGATION_ID=str(uuid4()),
    )
    endpoint = reverse("recommendations-history")
    assert client.delete(endpoint).status_code == 403
    response = client.delete(endpoint, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
    assert response.status_code == 204
    assert not Visitor.objects.exists()
    assert response.cookies["matchday_visitor"]["max-age"] == 0


def test_interest_propagates_through_actual_membership_and_slug_endpoint():
    team = Team.objects.create(name="Club")
    tournament = Tournament.objects.create(name="Cup", slug="cup", country="Chile", category="Cup")
    season = Season.objects.create(tournament=tournament, name="2026")
    season.teams.add(team)
    id, _ = record(team)
    injector_instance.get(ProcessRecommendationsUseCase).execute()
    profile = InterestProfile.objects.get(visitor_id=id)
    assert profile.tournament_weights[str(tournament.id)] > 0
    result = injector_instance.get(GetRecommendationsQuery).execute(visitor_id=id)
    assert result.tournaments[0].endpoint == reverse("tournaments-detail", args=["cup"])


def test_active_time_increases_affinity_and_is_bounded_per_content_day():
    team = Team.objects.create(name="Club")
    now = timezone.now().replace(hour=12)
    id, first = record(team, now=now - timedelta(minutes=5))
    _, second = record(team, visitor_id=id, now=now - timedelta(minutes=3))
    heartbeat = injector_instance.get(RecordActiveTimeUseCase)
    for navigation_id in (first, second):
        heartbeat.execute(
            visitor_id=id,
            navigation_id=navigation_id,
            content_kind=ContentKind.TEAM,
            content_id=team.id,
            active_seconds=120,
            now=now,
        )
    injector_instance.get(GenerateRecommendationsUseCase).execute(visitor_id=id, now=now)
    weight = InterestProfile.objects.get(visitor_id=id).team_weights[str(team.id)]
    assert 2.9 < weight <= 3  # one counted visit + two minutes, not four minutes


def test_three_visits_per_day_and_new_days_count_more_than_reloads():
    team = Team.objects.create(name="Club")
    now = timezone.now().replace(hour=12, minute=0, second=0)
    visitor_id = None
    for hours in range(5):
        visitor_id, _ = record(team, visitor_id=visitor_id, now=now + timedelta(hours=hours))
    assert NavigationActivity.objects.filter(counts_as_visit=True).count() == 3
    record(team, visitor_id=visitor_id, now=now + timedelta(days=1))
    assert NavigationActivity.objects.filter(counts_as_visit=True).count() == 4


def test_expired_history_is_purged_and_missing_entities_stop_affecting_profiles():
    now = timezone.now()
    old = Team.objects.create(name="Old")
    old_id, _ = record(old, now=now - timedelta(days=31))
    current = Team.objects.create(name="Current")
    current_id, _ = record(current, now=now)
    injector_instance.get(PurgeNavigationHistoryUseCase).execute(now=now)
    assert not Visitor.objects.filter(id=old_id).exists()
    assert Visitor.objects.filter(id=current_id).exists()
    current.delete()
    injector_instance.get(GenerateRecommendationsUseCase).execute(visitor_id=current_id)
    assert InterestProfile.objects.get(visitor_id=current_id).team_weights == {}


def test_anonymous_cold_start_does_not_create_a_profile_and_has_no_duplicates():
    Team.objects.create(name="Discovery")
    response = APIClient().get(reverse("recommendations-list"))
    assert response.status_code == 200
    assert not response.data["personalized"]
    assert "no-store" in response["Cache-Control"]
    assert not Visitor.objects.exists()
    items = [
        item
        for section in ("news", "matches", "tournaments", "discovery")
        for item in response.data[section]
    ]
    assert len(items) == len({(item["kind"], item["id"]) for item in items})


def test_worker_once_and_batch_limit():
    team = Team.objects.create(name="Club")
    for _ in range(3):
        record(team)
    output = StringIO()
    call_command("run_recommendations_worker", once=True, batch_size=2, stdout=output)
    assert InterestProfile.objects.count() == 2
    assert "2" in output.getvalue()
    call_command("run_recommendations_worker", once=True, batch_size=2, stdout=output)
    assert InterestProfile.objects.count() == 3


def test_content_lookup_is_batched_not_one_query_per_reference(django_assert_num_queries):
    teams = [Team.objects.create(name=f"Club {i}") for i in range(10)]
    references = [ContentReference(ContentKind.TEAM, team.id) for team in teams]
    with django_assert_num_queries(2):
        result = injector_instance.get(ContentQueryRepository).resolve(references)
    assert len(result) == 10


def test_feed_returns_immutable_dtos_and_serializes_without_database_reads(
    django_assert_num_queries,
):
    from dataclasses import FrozenInstanceError

    from modules.recommendations.api.contracts.responses.get_recommendations_response import (
        GetRecommendationsResponse,
    )

    team = Team.objects.create(name="Club", crest="teams/crests/club.webp")
    visitor_id, _ = record(team)
    injector_instance.get(ProcessRecommendationsUseCase).execute()
    feed = injector_instance.get(GetRecommendationsQuery).execute(visitor_id=visitor_id)
    with pytest.raises(FrozenInstanceError):
        feed.personalized = False
    with django_assert_num_queries(0):
        data = GetRecommendationsResponse(feed).data
    assert data["personalized"]
    items = [item for section in data.values() if isinstance(section, list) for item in section]
    assert all("image" in item for item in items)


def test_content_images_come_from_the_owner_entities():
    team = Team.objects.create(name="Club", crest="teams/crests/club.webp")
    news = News.objects.create(
        title="Noticia",
        content={"children": ["Contenido"]},
        cover_image="news/covers/noticia.webp",
        status=NewsStatus.PUBLISHED,
        published_at=timezone.now(),
    )
    tournament = Tournament.objects.create(
        slug="copa",
        name="Copa",
        country="Chile",
        category="Copa nacional",
        logo="tournaments/logos/copa.webp",
    )

    resolved = injector_instance.get(ContentQueryRepository).resolve(
        (
            ContentReference(ContentKind.TEAM, team.id),
            ContentReference(ContentKind.NEWS, news.id),
            ContentReference(ContentKind.TOURNAMENT, tournament.id),
        )
    )

    assert resolved[f"team:{team.id}"].image == "teams/crests/club.webp"
    assert resolved[f"news:{news.id}"].image == "news/covers/noticia.webp"
    assert resolved[f"tournament:{tournament.id}"].image == "tournaments/logos/copa.webp"
