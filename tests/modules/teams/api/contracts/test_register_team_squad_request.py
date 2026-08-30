import pytest

from modules.teams.api.contracts.requests.register_team_squad_request import (
    RegisterTeamSquadRequest,
)


def test_accepts_player_list():
    request = RegisterTeamSquadRequest(
        data={"players": [{"name": "Jugador uno"}, {"name": "Jugador dos"}]}
    )

    assert request.is_valid()
    assert len(request.validated_data["players"]) == 2


@pytest.mark.parametrize("data", [{}, {"players": []}])
def test_rejects_missing_or_empty_squad(data):
    request = RegisterTeamSquadRequest(data=data)

    assert not request.is_valid()
    assert "players" in request.errors
