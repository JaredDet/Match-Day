from datetime import UTC, datetime, timedelta

import pytest
from rest_framework.test import APIClient

from core.dependency_injector import injector_instance
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.domain.match import Match
from modules.matches.domain.penalty_shootout import PenaltyShootout
from modules.teams.domain.team import Team
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.domain.phase import Phase
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament

pytestmark = pytest.mark.django_db


@pytest.fixture
def cup():
    tournament = Tournament.objects.create(slug="cup", name="Cup", country="Chile", category="Cup")
    season = Season.objects.create(tournament=tournament, name="2026")
    teams = [Team.objects.create(name=f"Team {i}") for i in range(4)]
    season.teams.set(teams)
    return APIClient(), season, teams


def generate(client, season, teams, **extra):
    return client.post(
        f"/api/tournament-seasons/{season.id}/generate-bracket/",
        {
            "starts_at": "2026-10-01T12:00:00Z",
            "team_ids": [str(team.id) for team in teams],
            **extra,
        },
        format="json",
    )


def finish(match, home=1, away=0):
    match.start(match.scheduled_at)
    match.home_goal_count = home
    match.away_goal_count = away
    match.current_period = "second_half"
    match.current_minute = 90
    match.save()
    injector_instance.get(FinishMatchUseCase).execute(
        match.id, finished_at=match.scheduled_at + timedelta(hours=2)
    )


def test_generates_and_automatically_advances_with_third_place(
    cup, django_capture_on_commit_callbacks
):
    client, season, teams = cup
    response = generate(client, season, teams)
    assert response.status_code == 201, response.data
    assert len(response.data["phase_ids"]) == 3
    semifinals = Phase.objects.get(season=season, expected_matches=2)
    fixtures = list(
        Fixture.objects.filter(phase=semifinals).select_related("match").order_by("position")
    )
    assert [(f.match.home_team_id, f.match.away_team_id) for f in fixtures] == [
        (teams[0].id, teams[3].id),
        (teams[1].id, teams[2].id),
    ]

    with django_capture_on_commit_callbacks(execute=True):
        finish(fixtures[0].match)

    assert Fixture.objects.filter(phase__season=season).count() == 2

    with django_capture_on_commit_callbacks(execute=True):
        finish(fixtures[1].match, home=0, away=2)

    final = Fixture.objects.select_related("match").get(phase__season=season, phase__name="Final")
    third = Fixture.objects.select_related("match").get(
        phase__season=season, phase__kind="third_place"
    )
    assert (final.match.home_team_id, final.match.away_team_id) == (teams[0].id, teams[2].id)
    assert (third.match.home_team_id, third.match.away_team_id) == (teams[3].id, teams[1].id)
    assert final.match.scheduled_at == datetime(2026, 10, 8, 12, tzinfo=UTC)
    assert client.post(f"/api/tournament-seasons/{season.id}/advance-bracket/").data == {
        "created_matches": 0
    }
    assert generate(client, season, teams).status_code == 409
    assert client.delete(f"/api/tournament-fixtures/{final.id}/").status_code == 409
    assert (
        client.post(
            f"/api/tournament-seasons/{season.id}/teams/",
            {"team_id": str(teams[0].id)},
            format="json",
        ).status_code
        == 409
    )


def test_unresolved_draw_waits_for_finished_shootout(cup, django_capture_on_commit_callbacks):
    client, season, teams = cup
    assert generate(client, season, teams).status_code == 201
    fixtures = list(Fixture.objects.filter(phase__season=season).select_related("match"))

    with django_capture_on_commit_callbacks(execute=True):
        finish(fixtures[0].match, home=1, away=1)
        finish(fixtures[1].match)

    assert Fixture.objects.filter(phase__season=season).count() == 2

    with django_capture_on_commit_callbacks(execute=True):
        PenaltyShootout.objects.create(
            match=fixtures[0].match,
            status="finished",
            home_score=5,
            away_score=4,
            home_kick_count=5,
            away_kick_count=5,
            winner_team_side="home",
            finished_at=datetime(2026, 10, 1, 15, tzinfo=UTC),
        )

    assert Fixture.objects.filter(phase__season=season).count() == 4


@pytest.mark.parametrize("size", [2, 8, 16, 32, 64])
def test_supported_bracket_sizes(cup, size):
    client, season, teams = cup
    teams = teams[:size]

    while len(teams) < size:
        teams.append(Team.objects.create(name=f"Extra {len(teams)}"))

    season.teams.set(teams)
    assert generate(client, season, teams, third_place=False).status_code == 201
    assert Fixture.objects.filter(phase__season=season).count() == size // 2
    assert not Phase.objects.filter(season=season, kind="third_place").exists()


def test_invalid_entrants_and_atomic_rollback(cup):
    client, season, teams = cup
    assert generate(client, season, teams[:3]).status_code == 400
    assert generate(client, season, [teams[0], teams[0]]).status_code == 400
    assert not Phase.objects.filter(season=season).exists()
    collision = Match.schedule(
        home_team=teams[0], away_team=teams[3], scheduled_at=datetime(2026, 10, 1, 12, tzinfo=UTC)
    )
    collision.save()
    assert generate(client, season, teams).status_code == 409
    assert not Phase.objects.filter(season=season).exists()
    assert Match.objects.count() == 1


def test_generation_from_groups_blocks_unresolved_ties(cup):
    client, season, teams = cup
    phase = Phase.objects.create(
        season=season, name="Groups", kind="groups", order=1, status="finished", qualifying_teams=1
    )

    for index in range(2):
        group = Group.objects.create(phase=phase, name=str(index))
        pair = teams[index * 2 : index * 2 + 2]

        for team in pair:
            GroupEntry.objects.create(group=group, phase=phase, team=team)

        match = Match.schedule(
            home_team=pair[0], away_team=pair[1], scheduled_at=datetime(2026, 10, 1, 12, tzinfo=UTC)
        )
        match.save()
        finish(match, home=0, away=0)
        Fixture.objects.create(phase=phase, group=group, match=match, position=index)

    url = f"/api/tournament-seasons/{season.id}/generate-bracket/"
    payload = {"source_phase_id": str(phase.id), "starts_at": "2026-10-08T12:00:00Z"}
    response = client.post(url, payload, format="json")
    assert response.status_code == 409
    assert response.data["code"] == "tournament_unresolved_tie"

    for group in Group.objects.filter(phase=phase):
        ids = [str(entry.team_id) for entry in group.entries.order_by("team_id")]
        assert (
            client.put(
                f"/api/tournament-groups/{group.id}/tie-break/", {"team_ids": ids}, format="json"
            ).status_code
            == 204
        )

    response = client.post(url, payload, format="json")
    assert response.status_code == 201, response.data
    assert Phase.objects.filter(season=season, generated=True).count() == 1
    assert (
        client.put(
            f"/api/tournament-phases/{phase.id}/status/", {"status": "scheduled"}, format="json"
        ).status_code
        == 409
    )


def test_all_rounds_finish_automatically_and_retries_do_not_duplicate(
    cup, django_capture_on_commit_callbacks
):
    client, season, teams = cup
    teams += [Team.objects.create(name=f"Extra {i}") for i in range(4)]
    season.teams.set(teams)
    assert generate(client, season, teams).status_code == 201

    for _ in range(3):
        pending = list(
            Fixture.objects.filter(phase__season=season, match__status="scheduled").select_related(
                "match"
            )
        )

        assert pending

        for fixture in pending:
            with django_capture_on_commit_callbacks(execute=True):
                finish(fixture.match)

    assert Match.objects.count() == 8
    assert not Phase.objects.filter(season=season).exclude(status="finished").exists()
    assert client.post(f"/api/tournament-seasons/{season.id}/advance-bracket/").data == {
        "created_matches": 0
    }


def test_source_result_correction_reports_conflict_without_rewriting_final(
    cup, django_capture_on_commit_callbacks
):
    client, season, teams = cup
    assert generate(client, season, teams).status_code == 201
    fixtures = list(Fixture.objects.filter(phase__season=season).select_related("match"))

    for fixture in fixtures:
        with django_capture_on_commit_callbacks(execute=True):
            finish(fixture.match)

    final = Fixture.objects.get(phase__season=season, phase__name="Final")
    before = Match.objects.values().get(pk=final.match_id)
    # Simulate an administrative result correction; bulk update intentionally skips signals.
    Match.objects.filter(id=fixtures[0].match_id).update(home_goal_count=0, away_goal_count=2)
    response = client.post(f"/api/tournament-seasons/{season.id}/advance-bracket/")

    assert response.status_code == 409
    assert response.data["code"] == "tournament_advancement_conflict"
    assert Match.objects.values().get(pk=final.match_id) == before
