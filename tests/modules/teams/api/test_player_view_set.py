import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_lists_players_with_filters():
    team = Team.objects.create(name="Atlético Bahía")
    other_team = Team.objects.create(name="Deportivo Cordillera")
    captain = Player.objects.create(team=team, name="Mateo Rojas")
    Player.objects.create(team=other_team, name="Mateo Silva")
    team.captain = captain
    team.save()

    response = APIClient().get(
        reverse("players-list"),
        {"search": "mateo", "team_id": str(team.id)},
    )

    assert response.status_code == 200
    assert response.data == [
        {
            "id": str(captain.id),
            "name": "Mateo Rojas",
            "preferred_position": None,
            "preferred_shirt_number": None,
            "team": {"id": str(team.id), "name": "Atlético Bahía"},
            "is_captain": True,
            "appearances": 0,
            "goals": 0,
        }
    ]


def test_gets_player_detail():
    team = Team.objects.create(name="Atlético Bahía")
    player = Player.objects.create(team=team, name="Mateo Rojas")

    response = APIClient().get(reverse("players-detail", args=[player.id]))

    assert response.status_code == 200
    assert response.data == {
        "id": str(player.id),
        "name": "Mateo Rojas",
        "preferred_position": None,
        "preferred_shirt_number": None,
        "team": {"id": str(team.id), "name": "Atlético Bahía"},
        "is_captain": False,
        "statistics": {
            "appearances": 0,
            "goals": 0,
            "yellow_cards": 0,
            "red_cards": 0,
        },
        "recent_matches": [],
    }


def test_returns_not_found_when_getting_unknown_player():
    from uuid import UUID

    response = APIClient().get(reverse("players-detail", args=[UUID(int=0)]))

    assert response.status_code == 404
    assert response.data["code"] == "player_not_found"
