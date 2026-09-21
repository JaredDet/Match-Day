from datetime import timedelta
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from modules.news.domain.news import News, NewsStatus
from modules.recommendations.constants import VISITOR_COOKIE_NAME
from modules.recommendations.domain.navigation_activity import NavigationActivity
from modules.recommendations.domain.visitor import Visitor
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from modules.tournaments.domain.tournament import Tournament
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def navigate(client, url, navigation_id=None, **headers):
    return client.get(
        url,
        HTTP_X_NAVIGATION_INTENT="detail-view",
        HTTP_X_NAVIGATION_ID=str(navigation_id or uuid4()),
        **headers,
    )


@pytest.mark.parametrize("kind", ["team", "player", "news", "match", "tournament"])
def test_detail_get_records_the_resolved_entity(kind):
    team = Team.objects.create(name="Club")
    if kind == "team":
        entity, url = team, reverse("teams-detail", args=[team.id])
    elif kind == "player":
        entity = Player.objects.create(team=team, name="Player")
        url = reverse("players-detail", args=[entity.id])
    elif kind == "news":
        entity = News.objects.create(
            title="News",
            status=NewsStatus.PUBLISHED,
            content={"children": []},
            published_at=timezone.now(),
        )
        url = reverse("news-detail", args=[entity.id])
    elif kind == "match":
        entity = MatchMother.create(persist_teams=True)
        entity.save()
        url = reverse("matches-detail", args=[entity.id])
    else:
        entity = Tournament.objects.create(name="Cup", slug="cup", country="Chile", category="Cup")
        url = reverse("tournaments-detail", args=[entity.slug])
    client = APIClient()
    response = navigate(client, url)
    assert response.status_code == 200
    activity = NavigationActivity.objects.get()
    assert activity.content_kind == kind
    assert activity.content_id == entity.id
    cookie = response.cookies[VISITOR_COOKIE_NAME]
    assert cookie["httponly"]
    assert cookie["samesite"] == "Lax"
    assert "private" in response["Cache-Control"]
    assert "no-store" in response["Cache-Control"]
    assert "X-Navigation-Id" in response["Vary"]
    assert "csrftoken" in client.cookies


@pytest.mark.parametrize(
    "scenario", ["plain", "head", "list", "prefetch", "bad_uuid", "not_found", "draft", "scheduled"]
)
def test_non_navigation_requests_do_not_create_visitors(scenario):
    client = APIClient()
    team = Team.objects.create(name="Club")
    url = reverse("teams-detail", args=[team.id])
    if scenario == "plain":
        client.get(url)
    elif scenario == "head":
        client.head(url, HTTP_X_NAVIGATION_INTENT="detail-view", HTTP_X_NAVIGATION_ID=str(uuid4()))
    elif scenario == "list":
        navigate(client, reverse("teams-list"))
    elif scenario == "prefetch":
        navigate(client, url, HTTP_SEC_PURPOSE="prefetch")
    elif scenario == "bad_uuid":
        client.get(url, HTTP_X_NAVIGATION_INTENT="detail-view", HTTP_X_NAVIGATION_ID="invalid")
    elif scenario == "not_found":
        navigate(client, reverse("teams-detail", args=[uuid4()]))
    else:
        news = News.objects.create(
            title="Private", content={"children": []}, status=scenario.upper()
        )
        navigate(client, reverse("news-detail", args=[news.id]))
    assert not NavigationActivity.objects.exists()
    assert not Visitor.objects.exists()


def test_retries_are_idempotent_and_reloads_do_not_add_visit_weight():
    client = APIClient()
    team = Team.objects.create(name="Club")
    url = reverse("teams-detail", args=[team.id])
    id = uuid4()
    navigate(client, url, id)
    navigate(client, url, id)
    navigate(client, url)
    assert Visitor.objects.count() == 1
    assert NavigationActivity.objects.count() == 2
    assert NavigationActivity.objects.filter(counts_as_visit=True).count() == 1


def test_heartbeat_accumulates_time_once_and_requires_csrf():
    client = APIClient(enforce_csrf_checks=True)
    team = Team.objects.create(name="Club")
    id = uuid4()
    navigate(client, reverse("teams-detail", args=[team.id]), id)
    activity = NavigationActivity.objects.get()
    NavigationActivity.objects.filter(id=activity.id).update(
        occurred_at=timezone.now() - timedelta(seconds=60)
    )
    endpoint = reverse("recommendations-heartbeat")
    payload = {
        "navigation_id": str(id),
        "content_kind": "team",
        "content_id": str(team.id),
        "active_seconds": 30,
    }
    assert client.post(endpoint, payload, format="json").status_code == 403
    headers = {"HTTP_X_CSRFTOKEN": client.cookies["csrftoken"].value}
    for seconds in (30, 30, 15, 45):
        response = client.post(
            endpoint, {**payload, "active_seconds": seconds}, format="json", **headers
        )
        assert response.status_code == 204
    activity.refresh_from_db()
    assert activity.active_seconds == 45
    assert Visitor.objects.get().activity_version == 3
    # Beacon uses FormData because it cannot set the X-CSRFToken header.
    response = client.post(
        endpoint,
        {**payload, "active_seconds": 50, "csrfmiddlewaretoken": client.cookies["csrftoken"].value},
        format="multipart",
    )
    assert response.status_code == 204


@pytest.mark.parametrize("seconds", [-1, 121, 60, 1.5])
def test_heartbeat_rejects_invalid_or_impossible_elapsed_time(seconds):
    client = APIClient()
    team = Team.objects.create(name="Club")
    id = uuid4()
    navigate(client, reverse("teams-detail", args=[team.id]), id)
    response = client.post(
        reverse("recommendations-heartbeat"),
        {
            "navigation_id": str(id),
            "content_kind": "team",
            "content_id": str(team.id),
            "active_seconds": seconds,
        },
        format="json",
    )
    assert response.status_code == 400
    assert NavigationActivity.objects.get().active_seconds == 0


def test_a_visitor_cannot_update_someone_elses_activity_or_forge_cookie():
    team = Team.objects.create(name="Club")
    first, second = APIClient(), APIClient()
    navigation_id = uuid4()
    navigate(first, reverse("teams-detail", args=[team.id]), navigation_id)
    navigate(second, reverse("teams-detail", args=[team.id]))
    payload = {
        "navigation_id": str(navigation_id),
        "content_kind": "team",
        "content_id": str(team.id),
        "active_seconds": 1,
    }
    assert second.post(reverse("recommendations-heartbeat"), payload).status_code == 404
    second.cookies[VISITOR_COOKIE_NAME] = str(
        NavigationActivity.objects.get(navigation_id=navigation_id).visitor_id
    )
    assert second.post(reverse("recommendations-heartbeat"), payload).status_code == 404


def test_telemetry_failure_does_not_break_content_response():
    from unittest.mock import patch

    team = Team.objects.create(name="Club")
    with patch(
        "modules.recommendations.application.commands.record_navigation_use_case.RecordNavigationUseCase.execute",
        side_effect=RuntimeError("unavailable"),
    ):
        response = navigate(APIClient(), reverse("teams-detail", args=[team.id]))
    assert response.status_code == 200
    assert not Visitor.objects.exists()


@pytest.mark.parametrize("mismatch", ["kind", "id", "missing"])
def test_heartbeat_cannot_change_the_content_of_a_registered_visit(mismatch):
    client = APIClient()
    team = Team.objects.create(name="Club")
    navigation_id = uuid4()
    navigate(client, reverse("teams-detail", args=[team.id]), navigation_id)
    payload = {
        "navigation_id": str(navigation_id),
        "content_kind": "team",
        "content_id": str(team.id),
        "active_seconds": 1,
    }
    if mismatch == "kind":
        payload["content_kind"] = "news"
    elif mismatch == "id":
        payload["content_id"] = str(uuid4())
    else:
        del payload["content_kind"]
    response = client.post(reverse("recommendations-heartbeat"), payload, format="json")
    assert response.status_code == 400
    activity = NavigationActivity.objects.get()
    assert activity.active_seconds == 0
    assert activity.content_kind == "team"
    assert activity.content_id == team.id
