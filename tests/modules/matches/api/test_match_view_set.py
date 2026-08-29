from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from modules.matches.domain.card import CardType
from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.match_event import TeamSide

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


def test_registers_goal_and_updates_score_through_injected_use_case():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.save()

    response = APIClient().post(
        reverse("matches-register-goal", args=[match.id]),
        {
            "team_side": TeamSide.HOME,
            "player_name": "Goleador Local",
            "minute": 34,
        },
        format="json",
    )

    assert response.status_code == 201
    goal = match.goals.get(id=UUID(response.data["id"]))
    assert goal.player_name == "Goleador Local"
    match.refresh_from_db()
    assert match.home_goal_count == 1
    assert match.away_goal_count == 0


def test_rejects_goal_when_match_is_not_live():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()

    response = APIClient().post(
        reverse("matches-register-goal", args=[match.id]),
        {"team_side": TeamSide.HOME, "player_name": "Jugador", "minute": 1},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"
    assert match.goals.count() == 0


def test_registers_card_and_updates_counter_through_injected_use_case():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.save()

    response = APIClient().post(
        reverse("matches-register-card", args=[match.id]),
        {
            "team_side": TeamSide.AWAY,
            "player_name": "Defensor visitante",
            "card_type": CardType.RED,
            "minute": 80,
        },
        format="json",
    )

    assert response.status_code == 201
    card = match.cards.get(id=UUID(response.data["id"]))
    assert card.card_type == CardType.RED
    match.refresh_from_db()
    assert match.home_card_count == 0
    assert match.away_card_count == 1


def test_rejects_card_when_match_is_not_live():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()

    response = APIClient().post(
        reverse("matches-register-card", args=[match.id]),
        {
            "team_side": TeamSide.HOME,
            "player_name": "Jugador",
            "card_type": CardType.YELLOW,
            "minute": 1,
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"
    assert match.cards.count() == 0


def test_cancels_goal_and_decrements_score_through_injected_use_case():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    goal = match.register_goal(
        team_side=TeamSide.HOME,
        player_name="Goleador Local",
        minute=34,
    )
    match.save()
    goal.save()

    response = APIClient().post(reverse("matches-cancel-goal", args=[match.id, goal.id]))

    assert response.status_code == 204
    goal.refresh_from_db()
    match.refresh_from_db()
    assert goal.cancelled_at is not None
    assert match.home_goal_count == 0


def test_rejects_cancelling_goal_twice():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    goal = match.register_goal(
        team_side=TeamSide.AWAY,
        player_name="Goleador Visitante",
        minute=50,
    )
    match.save()
    goal.save()

    first_response = APIClient().post(reverse("matches-cancel-goal", args=[match.id, goal.id]))
    response = APIClient().post(reverse("matches-cancel-goal", args=[match.id, goal.id]))

    assert first_response.status_code == 204
    assert response.status_code == 409
    assert response.data["code"] == "goal_already_cancelled"
    match.refresh_from_db()
    assert match.away_goal_count == 0


def test_cancels_card_and_decrements_counter_through_injected_use_case():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    card = match.register_card(
        team_side=TeamSide.AWAY,
        player_name="Defensor Visitante",
        card_type=CardType.YELLOW,
        minute=51,
    )
    match.save()
    card.save()

    response = APIClient().post(reverse("matches-cancel-card", args=[match.id, card.id]))

    assert response.status_code == 204
    card.refresh_from_db()
    match.refresh_from_db()
    assert card.cancelled_at is not None
    assert match.away_card_count == 0


def test_rejects_cancelling_card_twice():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    card = match.register_card(
        team_side=TeamSide.HOME,
        player_name="Defensor Local",
        card_type=CardType.RED,
        minute=80,
    )
    match.save()
    card.save()

    first_response = APIClient().post(reverse("matches-cancel-card", args=[match.id, card.id]))
    response = APIClient().post(reverse("matches-cancel-card", args=[match.id, card.id]))

    assert first_response.status_code == 204
    assert response.status_code == 409
    assert response.data["code"] == "card_already_cancelled"
    match.refresh_from_db()
    assert match.home_card_count == 0


def test_gets_match_detail_with_unified_event_timeline():
    match = Match.schedule(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    goal = match.register_goal(
        team_side=TeamSide.HOME,
        player_name="Goleador Local",
        minute=30,
    )
    card = match.register_card(
        team_side=TeamSide.AWAY,
        player_name="Defensor Visitante",
        card_type=CardType.RED,
        minute=70,
    )
    match.save()
    goal.save()
    card.save()

    response = APIClient().get(reverse("matches-detail", args=[match.id]))

    assert response.status_code == 200
    assert response.data["status"] == MatchStatus.LIVE
    assert response.data["home_team"] == {"name": "Colo-Colo", "goals": 1}
    assert response.data["away_team"] == {
        "name": "Universidad de Chile",
        "goals": 0,
    }
    assert [event["type"] for event in response.data["events"]] == [
        "goal",
        "red_card",
    ]
    assert response.data["events"][0]["id"] == str(goal.id)


def test_returns_not_found_when_getting_unknown_match():
    response = APIClient().get(reverse("matches-detail", args=[uuid4()]))

    assert response.status_code == 404
    assert response.data["code"] == "match_not_found"


def test_lists_matches_filtered_by_status_and_date():
    included = Match.schedule(
        home_team_name="Equipo Local",
        away_team_name="Equipo Visitante",
        scheduled_at=datetime(2026, 8, 30, 20, tzinfo=UTC),
    )
    included.start()
    excluded = Match.schedule(
        home_team_name="Otro Local",
        away_team_name="Otro Visitante",
        scheduled_at=datetime(2026, 8, 31, 20, tzinfo=UTC),
    )
    excluded.start()
    included.save()
    excluded.save()

    response = APIClient().get(
        reverse("matches-list"),
        {"status": "live", "date": "2026-08-30"},
    )

    assert response.status_code == 200
    assert response.data == [
        {
            "id": str(included.id),
            "status": "live",
            "scheduled_at": "2026-08-30T20:00:00Z",
            "home_team": {"name": "Equipo Local", "goals": 0},
            "away_team": {"name": "Equipo Visitante", "goals": 0},
        }
    ]


def test_rejects_invalid_match_list_filters():
    response = APIClient().get(reverse("matches-list"), {"status": "paused"})

    assert response.status_code == 400
    assert response.data["code"] == "validation_error"
    assert "status" in response.data["details"]
