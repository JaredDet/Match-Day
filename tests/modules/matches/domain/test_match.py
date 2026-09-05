from datetime import UTC, datetime, timedelta
from datetime import timezone as datetime_timezone

import pytest
from django.utils import timezone

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.errors import MatchErrors
from modules.teams.domain.team import Team
from tests.mothers.matches.match_mother import MatchMother


def test_schedules_match_with_teams():
    scheduled_at = timezone.now() + timedelta(days=1)
    home_team = Team.create(name="Colo-Colo")
    away_team = Team.create(name="Universidad de Chile")

    match = Match.schedule(
        home_team=home_team,
        away_team=away_team,
        scheduled_at=scheduled_at,
    )

    assert match.home_team == home_team
    assert match.away_team == away_team
    assert match.home_team_name == home_team.name
    assert match.away_team_name == away_team.name
    assert match.scheduled_at == scheduled_at
    assert match.status == MatchStatus.SCHEDULED


def test_fixture_key_ignores_team_order_and_timezone_offset():
    home_team = Team.create(name="Colo-Colo")
    away_team = Team.create(name="Universidad de Chile")
    first = Match.schedule(
        home_team=home_team,
        away_team=away_team,
        scheduled_at=datetime(2026, 9, 1, 20, tzinfo=UTC),
    )
    second = Match.schedule(
        home_team=away_team,
        away_team=home_team,
        scheduled_at=datetime(
            2026,
            9,
            1,
            16,
            tzinfo=datetime_timezone(timedelta(hours=-4)),
        ),
    )

    assert first.fixture_key == second.fixture_key


def test_rejects_using_same_team_on_both_sides():
    team = Team.create(name="Colo-Colo")
    with pytest.raises(type(MatchErrors.InvalidTeams)) as exc_info:
        Match.schedule(
            home_team=team,
            away_team=team,
            scheduled_at=timezone.now(),
        )

    assert exc_info.value.code == "invalid_match_teams"


def test_starts_scheduled_match():
    match = MatchMother.create()
    started_at = timezone.now()

    match.start(started_at)

    assert match.status == MatchStatus.LIVE
    assert match.current_period == MatchPeriod.FIRST_HALF
    assert match.started_at == started_at
    assert match.finished_at is None


def test_updates_and_normalizes_optional_match_details():
    match = MatchMother.create()

    match.update_details(
        stadium_name="  Estadio   Monumental ",
        referee_name="  Piero   Maza ",
    )

    assert match.stadium_name == "Estadio Monumental"
    assert match.referee_name == "Piero Maza"


def test_updates_one_detail_without_changing_the_other():
    match = MatchMother.create()
    match.update_details(stadium_name="Estadio Nacional", referee_name="Árbitro")

    match.update_details(referee_name=None)

    assert match.stadium_name == "Estadio Nacional"
    assert match.referee_name is None


def test_cannot_start_match_twice():
    match = MatchMother.create(status=MatchStatus.LIVE)

    with pytest.raises(type(MatchErrors.InvalidState)):
        match.start()


def test_moves_from_first_half_through_halftime_to_second_half():
    match = MatchMother.create()
    match.start()

    match.end_first_half()
    assert match.current_period == MatchPeriod.HALFTIME

    match.start_second_half()
    assert match.current_period == MatchPeriod.SECOND_HALF


def test_cannot_finish_during_first_half_or_halftime():
    match = MatchMother.create()
    match.start()

    with pytest.raises(type(MatchErrors.InvalidPeriod)):
        match.finish()

    match.end_first_half()
    with pytest.raises(type(MatchErrors.InvalidPeriod)):
        match.finish()


def test_rejects_moving_clock_backwards():
    match = MatchMother.create()
    match.start()
    match.update_clock(expected_period=MatchPeriod.FIRST_HALF, minute=30)

    with pytest.raises(type(MatchErrors.ClockCannotGoBackwards)):
        match.update_clock(expected_period=MatchPeriod.FIRST_HALF, minute=29)


def test_finishes_live_match():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )
    finished_at = match.started_at + timedelta(hours=2)

    match.finish(finished_at)

    assert match.status == MatchStatus.FINISHED
    assert match.finished_at == finished_at


def test_cannot_finish_scheduled_match():
    match = MatchMother.create()

    with pytest.raises(type(MatchErrors.InvalidState)):
        match.finish()


def test_cannot_finish_before_start():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )

    with pytest.raises(type(MatchErrors.InvalidFinishTime)):
        match.finish(match.started_at - timedelta(seconds=1))
