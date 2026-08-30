from modules.teams.api.contracts.requests.list_teams_request import ListTeamsRequest


def test_accepts_optional_team_search():
    request = ListTeamsRequest(data={"search": "atlético"})

    assert request.is_valid()
    assert request.validated_data == {"search": "atlético"}


def test_defaults_team_search_to_none():
    request = ListTeamsRequest(data={})

    assert request.is_valid()
    assert request.validated_data == {"search": None}
