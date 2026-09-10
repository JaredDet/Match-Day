from uuid import uuid4

import pytest

from modules.matches.api.contracts.requests.start_penalty_shootout_request import (
    StartPenaltyShootoutRequest,
)
from modules.matches.domain.match_event import TeamSide


@pytest.mark.parametrize("team_side", TeamSide)
def test_parses_starting_team_side(team_side):
    request = StartPenaltyShootoutRequest(
        data={"starting_team_side": team_side.value},
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["starting_team_side"] is team_side


def test_rejects_invalid_starting_team_side():
    request = StartPenaltyShootoutRequest(
        data={"starting_team_side": "invalid"},
    )

    assert not request.is_valid()


def test_parses_equalization_excluded_player_ids():
    player_id = uuid4()
    request = StartPenaltyShootoutRequest(
        data={
            "starting_team_side": TeamSide.HOME.value,
            "equalization_excluded_player_ids": [str(player_id)],
        },
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["equalization_excluded_player_ids"] == [player_id]
