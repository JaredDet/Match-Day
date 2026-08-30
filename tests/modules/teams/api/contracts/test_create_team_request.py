import pytest

from modules.teams.api.contracts.requests.create_team_request import CreateTeamRequest


def test_accepts_team_name():
    request = CreateTeamRequest(data={"name": "Colo-Colo"})

    assert request.is_valid()
    assert request.validated_data == {"name": "Colo-Colo"}


@pytest.mark.parametrize("data", [{}, {"name": ""}, {"name": " "}])
def test_rejects_missing_or_blank_team_name(data):
    request = CreateTeamRequest(data=data)

    assert not request.is_valid()
    assert "name" in request.errors
