import pytest
from rest_framework.test import APIClient

from modules.teams.domain.team import Team
from modules.tournaments.constants import DEFAULT_MAX_TEAMS_PER_GROUP
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.domain.phase import Phase
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("limit", [None, 2])
def test_enforces_default_and_custom_group_capacity(limit):
    client = APIClient()
    payload = dict(slug="copa", name="Copa", country="Chile", category="Copa")

    if limit is not None:
        payload["max_teams_per_group"] = limit

    response = client.post("/api/tournaments/", payload, format="json")

    assert response.status_code == 201
    tournament = Tournament.objects.get(pk=response.data["id"])
    capacity = limit if limit is not None else DEFAULT_MAX_TEAMS_PER_GROUP
    assert tournament.max_teams_per_group == capacity
    assert client.get("/api/tournaments/copa/").data["max_teams_per_group"] == capacity
    season = Season.objects.create(tournament=tournament, name="2026")
    phase = Phase.objects.create(season=season, name="Grupos", kind="groups", order=1)
    group = Group.objects.create(phase=phase, name="A")
    other = Group.objects.create(phase=phase, name="B")
    teams = [Team.objects.create(name=f"Equipo {i}") for i in range(capacity + 1)]
    season.teams.set(teams)

    for team in teams[:capacity]:
        response = client.post(
            "/api/tournament-group-entries/",
            {"group": str(group.id), "team": str(team.id)},
            format="json",
        )
        assert response.status_code == 201

    response = client.post(
        "/api/tournament-group-entries/",
        {"group": str(group.id), "team": str(teams[-1].id)},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "tournament_group_full"
    assert GroupEntry.objects.filter(group=group).count() == capacity
    response = client.post(
        "/api/tournament-group-entries/",
        {"group": str(other.id), "team": str(teams[-1].id)},
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.parametrize("capacity", [0, -1, 32768, None])
def test_rejects_invalid_capacity(capacity):
    response = APIClient().post(
        "/api/tournaments/",
        dict(
            slug="copa", name="Copa", country="Chile", category="Copa", max_teams_per_group=capacity
        ),
        format="json",
    )

    assert response.status_code == 400
    assert not Tournament.objects.exists()
