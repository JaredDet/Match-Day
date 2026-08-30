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
            "team": {"id": str(team.id), "name": "Atlético Bahía"},
            "is_captain": True,
            "appearances": 0,
            "goals": 0,
        }
    ]
