import pytest

from modules.teams.api.contracts.requests.register_player_request import (
    RegisterPlayerRequest,
)


@pytest.mark.parametrize("data", [{}, {"name": ""}, {"name": " "}])
def test_rejects_missing_or_blank_player_name(data):
    request = RegisterPlayerRequest(data=data)

    assert not request.is_valid()
    assert "name" in request.errors


def test_accepts_player_name():
    request = RegisterPlayerRequest(data={"name": "Arturo Vidal"})

    assert request.is_valid()
