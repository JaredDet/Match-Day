from datetime import UTC, datetime, timedelta

import pytest

from modules.matches.domain.match_clock import MatchClockStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother


def test_calculates_server_clock_and_added_time_without_persisting_each_second():
    started_at = datetime(2026, 9, 13, 18, tzinfo=UTC)
    match = MatchMother.create()
    match.start(started_at)
    match.set_period_added_time(expected_period=MatchPeriod.FIRST_HALF, minutes=2)

    snapshot = match.clock_snapshot(started_at + timedelta(minutes=46, seconds=30))

    assert snapshot.status == MatchClockStatus.REGULATION_TIME_REACHED
    assert snapshot.minute == 45
    assert snapshot.second == 30
    assert snapshot.added_minute == 2
    assert snapshot.elapsed_seconds == 2790
    assert snapshot.remaining_seconds == 30
    assert snapshot.deadline_at == started_at + timedelta(minutes=47)
    assert snapshot.version == 2


def test_marks_announced_deadline_as_reached():
    started_at = datetime(2026, 9, 13, 18, tzinfo=UTC)
    match = MatchMother.create()
    match.start(started_at)
    match.set_period_added_time(expected_period=MatchPeriod.FIRST_HALF, minutes=3)

    snapshot = match.clock_snapshot(started_at + timedelta(minutes=48))

    assert snapshot.status == MatchClockStatus.DEADLINE_REACHED
    assert snapshot.remaining_seconds == 0


def test_rejects_closing_period_before_announced_deadline():
    started_at = datetime(2026, 9, 13, 18, tzinfo=UTC)
    match = MatchMother.create()
    match.start(started_at)

    with pytest.raises(type(MatchErrors.MatchPeriodCannotEndYet)):
        match.end_period(
            expected_period=MatchPeriod.FIRST_HALF,
            ended_at=started_at + timedelta(minutes=44),
        )


def test_closes_period_and_starts_next_period_with_a_new_clock_version():
    started_at = datetime(2026, 9, 13, 18, tzinfo=UTC)
    match = MatchMother.create()
    match.start(started_at)
    match.end_period(
        expected_period=MatchPeriod.FIRST_HALF,
        ended_at=started_at + timedelta(minutes=45),
    )

    halftime_snapshot = match.clock_snapshot(started_at + timedelta(minutes=50))
    match.start_period(
        MatchPeriod.SECOND_HALF,
        started_at + timedelta(minutes=60),
    )

    assert halftime_snapshot.status == MatchClockStatus.CLOSED
    assert match.current_period == MatchPeriod.SECOND_HALF
    assert match.period_ended_at is None
    assert match.clock_version == 3
