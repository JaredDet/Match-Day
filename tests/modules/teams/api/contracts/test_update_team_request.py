import pytest

from modules.teams.api.contracts.requests.update_team_request import UpdateTeamRequest


def test_accepts_team_name():
    request = UpdateTeamRequest(data={"name": "Nombre nuevo"})

    assert request.is_valid()
    assert request.validated_data == {"name": "Nombre nuevo"}


@pytest.mark.parametrize("data", [{}, {"name": ""}, {"name": " "}])
def test_rejects_missing_or_blank_team_name(data):
    request = UpdateTeamRequest(data=data)

    assert not request.is_valid()
    assert "name" in request.errors
