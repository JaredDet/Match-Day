from uuid import UUID

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

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
