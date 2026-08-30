from uuid import UUID

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


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


def test_squad_registration_is_atomic_when_player_is_duplicated():
    team = Team.objects.create(name="Colo-Colo")

    response = APIClient().post(
        reverse("teams-register-squad", args=[team.id]),
        {"players": [{"name": "Jugador"}, {"name": "jugador"}]},
        format="json",
    )

    assert response.status_code == 409
    assert Player.objects.filter(team=team).count() == 0
