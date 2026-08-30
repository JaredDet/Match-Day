import uuid

import pytest

from modules.matches.api.contracts.requests.set_match_lineup_request import (
    SetMatchLineupRequest,
)
from modules.matches.domain.match import MatchFormation


def _players(count=11):
    return [
        {
            "player_id": str(uuid.uuid4()),
            "shirt_number": index,
        }
        for index in range(1, count + 1)
    ]


def test_parses_formation_enum_and_players():
    captain_id = uuid.uuid4()
    request = SetMatchLineupRequest(
        data={
            "formation": "4-3-3",
            "captain_id": str(captain_id),
            "players": _players(),
        }
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["formation"] == MatchFormation.FOUR_THREE_THREE
    assert len(request.validated_data["players"]) == 11
    assert request.validated_data["captain_id"] == captain_id


@pytest.mark.parametrize("count", [0, 10, 12])
def test_rejects_lineup_without_exactly_eleven_players(count):
    request = SetMatchLineupRequest(data={"formation": "4-3-3", "players": _players(count)})

    assert not request.is_valid()
    assert "players" in request.errors


def test_rejects_unknown_formation():
    request = SetMatchLineupRequest(data={"formation": "4-4-3", "players": _players()})

    assert not request.is_valid()
    assert "formation" in request.errors
