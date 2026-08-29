from modules.matches.api.contracts.requests.register_goal_request import RegisterGoalRequest
from modules.matches.domain.match_event import TeamSide


def test_parses_team_side_string_as_enum():
    request = RegisterGoalRequest(
        data={"team_side": "home", "player_name": "Jugador", "minute": 10}
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["team_side"] is TeamSide.HOME


def test_rejects_unknown_team_side():
    request = RegisterGoalRequest(
        data={"team_side": "neutral", "player_name": "Jugador", "minute": 10}
    )

    assert not request.is_valid()
    assert "team_side" in request.errors
