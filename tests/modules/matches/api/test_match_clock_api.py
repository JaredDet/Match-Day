from datetime import timedelta

import pytest
from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from config.asgi import application
from modules.matches.domain.match_event import MatchPeriod
from tests.mothers.matches.match_mother import MatchMother


@pytest.mark.django_db
def test_manages_period_clock_through_explicit_endpoints():
    match = MatchMother.create(persist_teams=True)
    match.start(timezone.now() - timedelta(minutes=45))
    match.save()
    client = APIClient()

    added_time_response = client.patch(
        reverse("matches-set-period-added-time", args=[match.id]),
        {"expected_period": "first_half", "minutes": 0},
        format="json",
    )
    end_response = client.post(
        reverse("matches-end-period", args=[match.id]),
        {"expected_period": "first_half"},
        format="json",
    )
    start_response = client.post(
        reverse("matches-start-period", args=[match.id]),
        {"period": "second_half"},
        format="json",
    )

    assert added_time_response.status_code == 204
    assert end_response.status_code == 204
    assert start_response.status_code == 204
    match.refresh_from_db()
    assert match.current_period == MatchPeriod.SECOND_HALF
    assert match.period_started_at is not None
    assert match.period_ended_at is None


@pytest.mark.django_db(transaction=True)
def test_websocket_sends_authoritative_snapshot_when_client_connects():
    match = MatchMother.create(persist_teams=True)
    match.start(timezone.now() - timedelta(minutes=12))
    match.save()

    async def scenario():
        communicator = WebsocketCommunicator(
            application,
            f"/ws/matches/{match.id}/clock/",
        )
        connected, _ = await communicator.connect()
        message = await communicator.receive_json_from()
        await communicator.disconnect()
        return connected, message

    connected, message = async_to_sync(scenario)()

    assert connected is True
    assert message["type"] == "match.clock.snapshot"
    assert message["match_id"] == str(match.id)
    assert message["clock"]["period"] == "first_half"
    assert message["clock"]["minute"] >= 12
    assert message["clock"]["version"] == 1
