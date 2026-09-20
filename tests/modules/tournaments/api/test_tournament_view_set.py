from datetime import UTC, datetime
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from modules.matches.domain.match import Match
from modules.teams.domain.team import Team
from modules.tournaments.domain.season import Season

pytestmark = pytest.mark.django_db


@pytest.fixture
def competition():
    client = APIClient()

    def create(resource, **data):
        response = client.post(f"/api/{resource}/", data, format="json")
        assert response.status_code == 201, response.data
        assert set(response.data) == {"id"}
        lookup = data["slug"] if resource == "tournaments" else response.data["id"]
        detail = client.get(f"/api/{resource}/{lookup}/")
        assert detail.status_code == 200, detail.data
        return detail.data

    teams = [Team.objects.create(name=name) for name in ["Norte", "Sur", "Este"]]
    tournament = create(
        "tournaments",
        slug="copa-matchday",
        name="Copa Matchday",
        country="Chile",
        category="Copa nacional",
    )
    season = create(
        "tournament-seasons",
        tournament=tournament["id"],
        name="2026",
        teams=[str(t.id) for t in teams],
    )
    phase = create(
        "tournament-phases", season=season["id"], name="Grupos", kind="groups", order=1, matchdays=6
    )
    group = create("tournament-groups", phase=phase["id"], name="A")
    for team in teams[:2]:
        create("tournament-group-entries", group=group["id"], team=str(team.id))
    return client, create, teams, season, phase, group


def schedule(home, away, day=1):
    match = Match.schedule(
        home_team=home, away_team=away, scheduled_at=datetime(2026, 9, day, tzinfo=UTC)
    )
    match.save()
    return match


def test_standings_use_only_finished_matches_and_are_season_scoped(competition):
    client, create, teams, season, phase, group = competition
    finished = schedule(*teams[:2])
    finished.start(datetime(2026, 9, 1, tzinfo=UTC))
    finished.home_goal_count = 3
    finished.away_goal_count = 1
    finished.current_period = "second_half"
    finished.finish(datetime(2026, 9, 1, 2, tzinfo=UTC))
    finished.save()
    pending = schedule(*teams[:2], day=2)
    for position, match in enumerate([finished, pending], 1):
        create(
            "tournament-fixtures",
            phase=phase["id"],
            group=group["id"],
            match=str(match.id),
            position=position,
        )
    endpoint = f"/api/tournament-seasons/{season['id']}/groups/"
    rows = client.get(endpoint).data[0]["rows"]
    assert rows[0] == dict(
        id=str(teams[0].id),
        w=1,
        d=0,
        l=0,
        gf=3,
        ga=1,
        played=1,
        goal_difference=2,
        points=3,
        qualified=False,
    )
    assert rows[1]["l"] == 1
    response = client.put(
        f"/api/tournament-phases/{phase['id']}/status/", {"status": "finished"}, format="json"
    )
    assert response.status_code == 204
    assert client.get(endpoint).data[0]["rows"][0]["qualified"] is True
    other = create("tournament-seasons", tournament=season["tournament"], name="2025")
    assert client.get(f"/api/tournament-seasons/{other['id']}/groups/").data == []


def test_invalid_membership_and_fixture_use_application_errors(competition):
    client, create, teams, season, phase, group = competition
    second = create("tournament-groups", phase=phase["id"], name="B")
    response = client.post(
        "/api/tournament-group-entries/",
        {"group": second["id"], "team": str(teams[0].id)},
        format="json",
    )
    assert response.status_code == 409
    assert response.data["code"] == "tournament_group_entry_already_exists"
    outsider = Team.objects.create(name="Fuera")
    assert (
        client.post(
            "/api/tournament-group-entries/",
            {"group": group["id"], "team": str(outsider.id)},
            format="json",
        ).status_code
        == 400
    )
    match = schedule(teams[0], teams[2])
    payload = dict(phase=phase["id"], group=group["id"], match=str(match.id), position=1)
    response = client.post("/api/tournament-fixtures/", payload, format="json")
    assert response.status_code == 400
    assert response.data["code"] == "invalid_tournament_fixture_teams"
    assert client.get("/api/tournament-phases/?season=invalid").status_code == 400


def test_bracket_pending_scores_third_place_and_duplicate_match(competition):
    client, create, teams, season, phase, group = competition
    final = create("tournament-phases", season=season["id"], name="Final", kind="knockout", order=2)
    third = create(
        "tournament-phases", season=season["id"], name="Tercer puesto", kind="third_place", order=3
    )
    match = schedule(*teams[:2])
    payload = dict(phase=final["id"], match=str(match.id), position=1)
    create("tournament-fixtures", **payload)
    assert client.post("/api/tournament-fixtures/", payload, format="json").status_code == 409
    assert (
        client.post(
            "/api/tournament-groups/", {"phase": final["id"], "name": "X"}, format="json"
        ).status_code
        == 400
    )
    third_match = schedule(teams[0], teams[2], day=2)
    create("tournament-fixtures", phase=third["id"], match=str(third_match.id), position=1)
    data = client.get(f"/api/tournament-seasons/{season['id']}/bracket/").data
    assert [r["name"] for r in data["rounds"]] == ["Final"]
    assert data["rounds"][0]["ties"][0]["homeScore"] is None
    assert data["third"]["id"] == str(third_match.id)
    assert client.get("/api/tournaments/copa-matchday/").status_code == 200
    tournaments = client.get("/api/tournaments/")
    assert tournaments.status_code == 200
    assert [tournament["slug"] for tournament in tournaments.data] == ["copa-matchday"]
    assert client.get("/api/tournaments/missing/").status_code == 404


@pytest.mark.parametrize("action", ["", "groups/", "bracket/", "matches/"])
def test_unknown_season_returns_application_not_found(action):
    response = APIClient().get(f"/api/tournament-seasons/{uuid4()}/{action}")

    assert response.status_code == 404
    assert response.data["code"] == "tournament_season_not_found"


def test_season_creation_rolls_back_when_a_team_is_missing(competition):
    client, create, teams, season, phase, group = competition
    before = Season.objects.count()

    response = client.post(
        "/api/tournament-seasons/",
        {
            "tournament": season["tournament"],
            "name": "2027",
            "teams": [str(teams[0].id), str(uuid4())],
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["code"] == "team_not_found"
    assert Season.objects.count() == before


@pytest.mark.parametrize("duplicate", ["season", "phase_order", "third_place", "group_name"])
def test_structure_duplicates_return_conflict(competition, duplicate):
    client, create, teams, season, phase, group = competition

    if duplicate == "season":
        resource = "tournament-seasons"
        data = {"tournament": season["tournament"], "name": season["name"]}
    elif duplicate == "phase_order":
        resource = "tournament-phases"
        data = {
            "season": season["id"],
            "name": "Otra fase",
            "kind": "knockout",
            "order": phase["order"],
        }
    elif duplicate == "third_place":
        resource = "tournament-phases"
        create(resource, season=season["id"], name="Tercero", kind="third_place", order=2)
        data = {"season": season["id"], "name": "Otro tercero", "kind": "third_place", "order": 3}
    else:
        resource = "tournament-groups"
        data = {"phase": phase["id"], "name": group["name"]}

    response = client.post(f"/api/{resource}/", data, format="json")

    assert response.status_code == 409
    assert response.data["code"].endswith("already_exists")


def test_fixture_listing_is_scoped_to_season_and_rejects_occupied_position(competition):
    client, create, teams, season, phase, group = competition
    first = schedule(*teams[:2])
    second = schedule(*teams[:2], day=2)
    fixture = create(
        "tournament-fixtures", phase=phase["id"], group=group["id"], match=str(first.id), position=1
    )

    response = client.post(
        "/api/tournament-fixtures/",
        {"phase": phase["id"], "group": group["id"], "match": str(second.id), "position": 1},
        format="json",
    )

    assert response.status_code == 409
    assert client.get(f"/api/tournament-seasons/{season['id']}/matches/").data == [fixture]

    other = create("tournament-seasons", tournament=season["tournament"], name="2025")

    assert client.get(f"/api/tournament-seasons/{other['id']}/matches/").data == []


def test_standings_count_draws_and_away_wins_and_recompute_results(competition):
    client, create, teams, season, phase, group = competition
    for day, scores in [(1, (1, 1)), (2, (0, 2))]:
        match = schedule(*teams[:2], day=day)
        match.start(datetime(2026, 9, day, tzinfo=UTC))
        match.home_goal_count, match.away_goal_count = scores
        match.current_period = "second_half"
        match.finish(datetime(2026, 9, day, 2, tzinfo=UTC))
        match.save()
        create(
            "tournament-fixtures",
            phase=phase["id"],
            group=group["id"],
            match=str(match.id),
            position=day,
        )

    endpoint = f"/api/tournament-seasons/{season['id']}/groups/"
    rows = client.get(endpoint).data[0]["rows"]

    assert [row["id"] for row in rows] == [str(teams[1].id), str(teams[0].id)]
    assert [(row["w"], row["d"], row["l"], row["points"]) for row in rows] == [
        (1, 1, 0, 4),
        (0, 1, 1, 1),
    ]

    match.home_goal_count, match.away_goal_count = 3, 0
    match.save()

    assert client.get(endpoint).data[0]["rows"][0]["id"] == str(teams[0].id)
