import pytest

from modules.teams.api.contracts.requests.update_player_request import UpdatePlayerRequest


def test_accepts_player_name():
    request = UpdatePlayerRequest(data={"name": "Nombre nuevo"})

    assert request.is_valid(), request.errors


@pytest.mark.parametrize("name", ["", None])
def test_rejects_invalid_player_name(name):
    request = UpdatePlayerRequest(data={"name": name})

    assert not request.is_valid()
    assert "name" in request.errors
