from datetime import timedelta
from uuid import UUID

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
