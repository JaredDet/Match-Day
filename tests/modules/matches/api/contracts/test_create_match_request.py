from datetime import timedelta

from django.utils import timezone

from modules.matches.api.contracts.requests.create_match_request import CreateMatchRequest


def test_accepts_create_match_request():
    scheduled_at = timezone.now() + timedelta(days=1)
    request = CreateMatchRequest(
        data={
            "home_team_name": "Colo-Colo",
            "away_team_name": "Universidad de Chile",
            "scheduled_at": scheduled_at.isoformat(),
        }
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["scheduled_at"] == scheduled_at


def test_rejects_request_without_scheduled_at():
    request = CreateMatchRequest(
        data={
            "home_team_name": "Colo-Colo",
            "away_team_name": "Universidad de Chile",
        }
    )

    assert not request.is_valid()
    assert "scheduled_at" in request.errors


def test_rejects_non_iso_8601_datetime():
    request = CreateMatchRequest(
        data={
            "home_team_name": "Colo-Colo",
            "away_team_name": "Universidad de Chile",
            "scheduled_at": "30/08/2026 20:00",
        }
    )

    assert not request.is_valid()
    assert "scheduled_at" in request.errors
