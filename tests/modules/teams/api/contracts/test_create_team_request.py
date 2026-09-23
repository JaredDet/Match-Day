import pytest

from modules.teams.api.contracts.requests.create_team_request import CreateTeamRequest


def test_accepts_team_name():
    request = CreateTeamRequest(data={"name": "Colo-Colo", "head_coach_name": "Jorge Almiron"})

    assert request.is_valid()
    assert request.validated_data == {
        "name": "Colo-Colo",
        "head_coach_name": "Jorge Almiron",
    }


@pytest.mark.parametrize("data", [{}, {"name": ""}, {"name": " "}])
def test_rejects_missing_or_blank_team_name(data):
    request = CreateTeamRequest(data=data)

    assert not request.is_valid()
    assert "name" in request.errors


@pytest.mark.parametrize("head_coach_name", [None, "", " "])
def test_rejects_missing_or_blank_head_coach(head_coach_name):
    data = {"name": "Colo-Colo"}
    if head_coach_name is not None:
        data["head_coach_name"] = head_coach_name
    request = CreateTeamRequest(data=data)

    assert not request.is_valid()
    assert "head_coach_name" in request.errors
