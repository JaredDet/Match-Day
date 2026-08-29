from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from modules.matches.domain.match import Match, MatchStatus

pytestmark = pytest.mark.django_db


def test_creates_match_through_injected_use_case():
    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_name": "  Colo-Colo ",
            "away_team_name": " Universidad de Chile ",
            "scheduled_at": (timezone.now() + timedelta(days=1)).isoformat(),
        },
        format="json",
    )

    assert response.status_code == 201
    match_id = UUID(response.data["id"])
    match = Match.objects.get(id=match_id)
    assert match.home_team_name == "Colo-Colo"
    assert match.away_team_name == "Universidad de Chile"
    assert match.status == MatchStatus.SCHEDULED


def test_returns_domain_error_when_teams_are_equal():
    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_name": "Colo-Colo",
            "away_team_name": "colo-colo",
            "scheduled_at": (timezone.now() + timedelta(days=1)).isoformat(),
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {
        "code": "invalid_match_teams",
        "message": "Los equipos deben tener nombres válidos y ser diferentes",
    }


def test_rejects_duplicate_match_with_reversed_teams():
    scheduled_at = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
    Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=scheduled_at,
    ).save()

    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_name": "universidad de chile",
            "away_team_name": "COLO-COLO",
            "scheduled_at": scheduled_at.isoformat(),
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "match_already_exists"


def test_formats_invalid_request_with_common_error_contract():
    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_name": "Colo-Colo",
            "away_team_name": "Universidad de Chile",
            "scheduled_at": "not-a-date",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "validation_error"
    assert "scheduled_at" in response.data["details"]


def test_starts_scheduled_match_through_injected_use_case():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now() + timedelta(hours=1),
    )
    match.save()

    response = APIClient().post(reverse("matches-start", args=[match.id]))

    assert response.status_code == 204
    assert response.content == b""
    match.refresh_from_db()
    assert match.status == MatchStatus.LIVE
    assert match.started_at is not None


def test_rejects_starting_match_twice():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.save()

    response = APIClient().post(reverse("matches-start", args=[match.id]))

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"


def test_returns_not_found_when_starting_unknown_match():
    response = APIClient().post(reverse("matches-start", args=[uuid4()]))

    assert response.status_code == 404
    assert response.data["code"] == "match_not_found"


def test_finishes_live_match_through_injected_use_case():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.save()

    response = APIClient().post(reverse("matches-finish", args=[match.id]))

    assert response.status_code == 204
    assert response.content == b""
    match.refresh_from_db()
    assert match.status == MatchStatus.FINISHED
    assert match.finished_at is not None


def test_rejects_finishing_match_that_is_not_live():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()

    response = APIClient().post(reverse("matches-finish", args=[match.id]))

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"


def test_returns_not_found_when_finishing_unknown_match():
    response = APIClient().post(reverse("matches-finish", args=[uuid4()]))

    assert response.status_code == 404
    assert response.data["code"] == "match_not_found"
