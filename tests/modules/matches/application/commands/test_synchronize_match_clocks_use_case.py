from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.utils import timezone

from modules.matches.application.commands.synchronize_match_clocks_use_case import (
    SynchronizeMatchClocksUseCase,
)
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from tests.mothers.matches.match_mother import MatchMother


@pytest.mark.django_db(transaction=True)
def test_monitor_publishes_snapshot_and_each_clock_alert_only_once():
    match = MatchMother.create(persist_teams=True)
    match.start(timezone.now() - timedelta(minutes=46))
    match.set_period_added_time(expected_period=MatchPeriod.FIRST_HALF, minutes=2)
    match.save()
    publisher = Mock()
    use_case = SynchronizeMatchClocksUseCase(MatchRepository(), publisher)

    assert use_case.execute() == 1

    match.refresh_from_db()
    assert match.regulation_time_alerted_at is not None
    assert match.period_deadline_alerted_at is None
    publisher.publish_snapshot.assert_called_once()
    publisher.publish_alert.assert_called_once()
    assert publisher.publish_alert.call_args.args[1] == "regulation_time_reached"

    publisher.reset_mock()
    match.period_started_at = timezone.now() - timedelta(minutes=48)
    match.save()

    use_case.execute()
    use_case.execute()

    match.refresh_from_db()
    assert match.period_deadline_alerted_at is not None
    assert publisher.publish_snapshot.call_count == 2
    publisher.publish_alert.assert_called_once()
    assert publisher.publish_alert.call_args.args[1] == "period_deadline_reached"
