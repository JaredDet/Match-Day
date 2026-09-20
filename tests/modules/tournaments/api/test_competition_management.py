from datetime import UTC, datetime
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from modules.matches.domain.match import Match
from modules.teams.domain.team import Team
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.domain.phase import Phase
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup():
    tournament = Tournament.objects.create(slug="cup", name="Cup", country="Chile", category="Cup")
    season = Season.objects.create(tournament=tournament, name="2026")
    phase = Phase.objects.create(season=season, name="Groups", kind="groups", order=1, matchdays=3)
    group = Group.objects.create(phase=phase, name="A")
    teams = [Team.objects.create(name=f"Team {i}") for i in range(4)]
    season.teams.set(teams)
    entries = [GroupEntry.objects.create(group=group, phase=phase, team=team) for team in teams]
    return APIClient(), season, phase, group, teams, entries


def test_add_remove_team_is_idempotent_and_protects_membership(setup):
    client, season, phase, group, teams, entries = setup
    team = Team.objects.create(name="New")
    url = f"/api/tournament-seasons/{season.id}/teams/"

    for _ in range(2):
        assert client.post(url, {"team_id": str(team.id)}, format="json").status_code == 204

    assert season.teams.count() == 5
    assert client.delete(url + f"{teams[0].id}/").status_code == 409

    for _ in range(2):
        assert client.delete(url + f"{team.id}/").status_code == 204

    assert season.teams.count() == 4
    assert client.post(url, {"team_id": str(uuid4())}, format="json").status_code == 404


def test_edit_and_delete_structure_in_dependency_order(setup):
    client, season, phase, group, teams, entries = setup
    phase_url = f"/api/tournament-phases/{phase.id}/"
    group_url = f"/api/tournament-groups/{group.id}/"
    assert (
        client.patch(phase_url, {"name": "Grupos", "matchdays": 4}, format="json").status_code
        == 204
    )
    assert client.patch(group_url, {"name": "B"}, format="json").status_code == 204
    assert client.patch(phase_url, {"kind": "knockout"}, format="json").status_code == 409
    assert client.delete(group_url).status_code == 409
    assert client.delete(phase_url).status_code == 409

    for entry in entries:
        assert client.delete(f"/api/tournament-group-entries/{entry.id}/").status_code == 204

    assert client.delete(group_url).status_code == 204
    assert client.delete(phase_url).status_code == 204


def test_fixture_update_revalidates_and_delete_preserves_match(setup):
    client, season, phase, group, teams, entries = setup
    match = Match.schedule(
        home_team=teams[0], away_team=teams[1], scheduled_at=datetime(2026, 9, 1, tzinfo=UTC)
    )
    match.save()
    fixture = Fixture.objects.create(phase=phase, group=group, match=match, position=1)
    url = f"/api/tournament-fixtures/{fixture.id}/"

    assert client.patch(url, {"position": 2, "matchday": 2}, format="json").status_code == 204
    fixture.refresh_from_db()
    assert (fixture.position, fixture.matchday) == (2, 2)
    assert client.patch(url, {"matchday": 4}, format="json").status_code == 400
    assert client.patch(url, {"group": None}, format="json").status_code == 400
    assert client.delete(f"/api/tournament-group-entries/{entries[0].id}/").status_code == 409
    assert client.delete(url).status_code == 204
    assert Match.objects.filter(id=match.id).exists()


def test_started_match_protects_structure(setup):
    client, season, phase, group, teams, entries = setup
    match = Match.schedule(
        home_team=teams[0], away_team=teams[1], scheduled_at=datetime(2026, 9, 1, tzinfo=UTC)
    )
    match.start(datetime(2026, 9, 1, tzinfo=UTC))
    match.save()
    fixture = Fixture.objects.create(phase=phase, group=group, match=match, position=1)

    for resource, entity in [
        ("tournament-fixtures", fixture),
        ("tournament-groups", group),
        ("tournament-phases", phase),
        ("tournament-group-entries", entries[0]),
    ]:
        assert client.delete(f"/api/{resource}/{entity.id}/").status_code == 409

    assert (
        client.patch(f"/api/tournament-phases/{phase.id}/", {"order": 8}, format="json").status_code
        == 409
    )


def test_manual_tie_order_requires_exact_participants_and_is_cleared_on_removal(setup):
    client, season, phase, group, teams, entries = setup
    url = f"/api/tournament-groups/{group.id}/tie-break/"
    assert client.put(url, {"team_ids": [str(teams[0].id)]}, format="json").status_code == 400
    assert (
        client.put(
            url, {"team_ids": [str(team.id) for team in reversed(teams)]}, format="json"
        ).status_code
        == 204
    )
    rows = client.get(f"/api/tournament-seasons/{season.id}/groups/").data[0]["rows"]
    assert [row["id"] for row in rows] == [str(team.id) for team in reversed(teams)]
    assert all("tie_break_required" not in row for row in rows)
    assert client.delete(f"/api/tournament-group-entries/{entries[0].id}/").status_code == 204
    group.refresh_from_db()
    assert group.tie_break_order == []
