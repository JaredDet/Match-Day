from datetime import UTC, datetime
from uuid import UUID

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from modules.matches.domain.match import Match
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_lists_teams_with_last_result_and_next_match():
    home_team = Team.objects.create(name="Atlético Bahía")
    away_team = Team.objects.create(name="Deportivo Cordillera")
    finished = Match.schedule(
        home_team=home_team,
        away_team=away_team,
        scheduled_at=datetime(2026, 8, 30, 20, tzinfo=UTC),
    )
    finished.start(datetime(2026, 8, 30, 20, tzinfo=UTC))
    finished.home_goal_count = 2
    finished.away_goal_count = 1
    finished.finish(datetime(2026, 8, 30, 22, tzinfo=UTC))
    finished.save()

    response = APIClient().get(reverse("teams-list"), {"search": "atlético"})

    assert response.status_code == 200
    assert response.data == [
        {
            "id": str(home_team.id),
            "name": "Atlético Bahía",
            "last_match": {
                "match_id": str(finished.id),
                "opponent_name": "Deportivo Cordillera",
                "goals_for": 2,
                "goals_against": 1,
                "result": "win",
            },
            "next_match": None,
        }
    ]


def test_gets_team_detail_with_statistics_and_current_players():
    home_team = Team.objects.create(name="Atlético Bahía")
    away_team = Team.objects.create(name="Deportivo Cordillera")
    player = Player.objects.create(team=home_team, name="Mateo Rojas")
    finished = Match.schedule(
        home_team=home_team,
        away_team=away_team,
        scheduled_at=datetime(2026, 8, 30, 20, tzinfo=UTC),
    )
    finished.start(datetime(2026, 8, 30, 20, tzinfo=UTC))
    finished.home_goal_count = 2
    finished.away_goal_count = 1
    finished.finish(datetime(2026, 8, 30, 22, tzinfo=UTC))
    finished.save()

    response = APIClient().get(reverse("teams-detail", args=[home_team.id]))

    assert response.status_code == 200
    assert response.data["id"] == str(home_team.id)
    assert response.data["statistics"] == {
        "matches_played": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "goals_for": 2,
        "goals_against": 1,
    }
    assert response.data["players"] == [
        {
            "id": str(player.id),
            "name": "Mateo Rojas",
            "preferred_position": None,
            "preferred_shirt_number": None,
            "is_captain": False,
        }
    ]
    assert response.data["recent_matches"][0]["result"] == "win"


def test_returns_not_found_when_getting_unknown_team():
    response = APIClient().get(reverse("teams-detail", args=[UUID(int=0)]))

    assert response.status_code == 404
    assert response.data["code"] == "team_not_found"


def test_creates_team_through_injected_use_case():
    response = APIClient().post(
        reverse("teams-list"),
        {"name": "  Colo-Colo  "},
        format="json",
    )

    assert response.status_code == 201
    team = Team.objects.get(id=UUID(response.data["id"]))
    assert team.name == "Colo-Colo"


def test_rejects_duplicate_team_name_case_insensitively():
    Team.objects.create(name="Colo-Colo")

    response = APIClient().post(
        reverse("teams-list"),
        {"name": "colo-colo"},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "team_already_exists"


def test_updates_team_through_injected_use_case():
    team = Team.objects.create(name="Nombre anterior")

    response = APIClient().patch(
        reverse("teams-detail", args=[team.id]),
        {"name": "  Nombre   nuevo  "},
        format="json",
    )

    assert response.status_code == 204
    team.refresh_from_db()
    assert team.name == "Nombre nuevo"


def test_returns_not_found_when_updating_unknown_team():
    response = APIClient().patch(
        reverse("teams-detail", args=[UUID(int=0)]),
        {"name": "Nombre nuevo"},
        format="json",
    )

    assert response.status_code == 404
    assert response.data["code"] == "team_not_found"


def test_rejects_duplicate_name_when_updating_team():
    Team.objects.create(name="Nombre ocupado")
    team = Team.objects.create(name="Nombre anterior")

    response = APIClient().patch(
        reverse("teams-detail", args=[team.id]),
        {"name": "nombre ocupado"},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "team_already_exists"


def test_registers_player_for_team():
    team = Team.objects.create(name="Colo-Colo")

    response = APIClient().post(
        reverse("teams-register-player", args=[team.id]),
        {"name": "Arturo Vidal"},
        format="json",
    )

    assert response.status_code == 201
    player = Player.objects.get(id=UUID(response.data["id"]))
    assert player.team == team
    assert player.name == "Arturo Vidal"


def test_updates_player_from_team():
    team = Team.objects.create(name="Colo-Colo")
    player = Player.objects.create(team=team, name="Nombre anterior")

    response = APIClient().patch(
        reverse("teams-update-player", args=[team.id, player.id]),
        {"name": "  Nombre   nuevo  "},
        format="json",
    )

    assert response.status_code == 204
    player.refresh_from_db()
    assert player.name == "Nombre nuevo"


def test_does_not_update_player_through_another_team():
    team = Team.objects.create(name="Colo-Colo")
    other_team = Team.objects.create(name="Universidad de Chile")
    player = Player.objects.create(team=other_team, name="Jugador rival")

    response = APIClient().patch(
        reverse("teams-update-player", args=[team.id, player.id]),
        {"name": "Nombre nuevo"},
        format="json",
    )

    assert response.status_code == 404
    assert response.data["code"] == "player_not_found"


def test_registers_complete_team_squad():
    team = Team.objects.create(name="Colo-Colo")

    response = APIClient().post(
        reverse("teams-register-squad", args=[team.id]),
        {"players": [{"name": "Jugador uno"}, {"name": "Jugador dos"}]},
        format="json",
    )

    assert response.status_code == 201
    assert Player.objects.filter(team=team).count() == 2
    assert len(response.data["ids"]) == 2


def test_sets_permanent_team_captain():
    team = Team.objects.create(name="Colo-Colo")
    player = Player.objects.create(team=team, name="Arturo Vidal")

    response = APIClient().put(
        reverse("teams-set-captain", args=[team.id]),
        {"player_id": str(player.id)},
        format="json",
    )

    assert response.status_code == 204
    team.refresh_from_db()
    assert team.captain == player


def test_rejects_captain_from_another_team():
    team = Team.objects.create(name="Colo-Colo")
    other_team = Team.objects.create(name="Universidad de Chile")
    player = Player.objects.create(team=other_team, name="Jugador rival")

    response = APIClient().put(
        reverse("teams-set-captain", args=[team.id]),
        {"player_id": str(player.id)},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "invalid_team_captain"


def test_squad_registration_is_atomic_when_player_is_duplicated():
    team = Team.objects.create(name="Colo-Colo")

    response = APIClient().post(
        reverse("teams-register-squad", args=[team.id]),
        {"players": [{"name": "Jugador"}, {"name": "jugador"}]},
        format="json",
    )

    assert response.status_code == 409
    assert Player.objects.filter(team=team).count() == 0
