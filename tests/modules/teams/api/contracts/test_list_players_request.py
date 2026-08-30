from uuid import uuid4

from modules.teams.api.contracts.requests.list_players_request import ListPlayersRequest


def test_accepts_optional_player_filters():
    team_id = uuid4()
    request = ListPlayersRequest(data={"search": "mateo", "team_id": str(team_id)})

    assert request.is_valid(), request.errors
    assert request.validated_data == {"search": "mateo", "team_id": team_id}


def test_defaults_player_filters_to_none():
    request = ListPlayersRequest(data={})

    assert request.is_valid(), request.errors
    assert request.validated_data == {"search": None, "team_id": None}
