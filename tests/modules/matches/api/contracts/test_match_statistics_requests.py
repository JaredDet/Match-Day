from uuid import uuid4

import pytest

from modules.matches.api.contracts.requests.register_shot_request import (
    RegisterShotRequest,
)
from modules.matches.api.contracts.requests.update_match_possession_request import (
    UpdateMatchPossessionRequest,
)
from modules.matches.domain.shot import ShotOutcome


def test_parses_saved_shot():
    goalkeeper_id = uuid4()
    request = RegisterShotRequest(
        data={
            "player_id": str(uuid4()),
            "goalkeeper_id": str(goalkeeper_id),
            "outcome": "saved",
            "minute": 20,
        }
    )

    assert request.is_valid()
    assert request.validated_data["outcome"] == ShotOutcome.SAVED
    assert request.validated_data["goalkeeper_id"] == goalkeeper_id


@pytest.mark.parametrize(
    "data",
    [
        {"player_id": str(uuid4()), "outcome": "saved", "minute": 20},
        {
            "player_id": str(uuid4()),
            "goalkeeper_id": str(uuid4()),
            "outcome": "off_target",
            "minute": 20,
        },
    ],
)
def test_rejects_inconsistent_shot_goalkeeper(data):
    request = RegisterShotRequest(data=data)

    assert not request.is_valid()


@pytest.mark.parametrize("percentage", [0, 50, 100])
def test_accepts_possession_percentage(percentage):
    request = UpdateMatchPossessionRequest(data={"home_percentage": percentage})

    assert request.is_valid()
