from uuid import uuid4

from modules.matches.api.contracts.requests.register_goal_request import RegisterGoalRequest


def test_parses_player_id():
    player_id = uuid4()
    request = RegisterGoalRequest(data={"player_id": str(player_id), "minute": 10})

    assert request.is_valid(), request.errors
    assert request.validated_data["player_id"] == player_id


def test_rejects_invalid_player_id():
    request = RegisterGoalRequest(data={"player_id": "invalid", "minute": 10})

    assert not request.is_valid()
    assert "player_id" in request.errors
