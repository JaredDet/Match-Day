import pytest

from modules.teams.api.contracts.requests.update_team_request import UpdateTeamRequest


def test_accepts_team_name():
    request = UpdateTeamRequest(data={"name": "Nombre nuevo", "head_coach_name": "Tecnico nuevo"})

    assert request.is_valid()
    assert request.validated_data == {
        "name": "Nombre nuevo",
        "head_coach_name": "Tecnico nuevo",
    }


@pytest.mark.parametrize("data", [{}, {"name": ""}, {"name": " "}])
def test_rejects_empty_update(data):
    request = UpdateTeamRequest(data=data)

    assert not request.is_valid()


def test_rejects_clearing_head_coach():
    request = UpdateTeamRequest(data={"head_coach_name": None})

    assert not request.is_valid()
