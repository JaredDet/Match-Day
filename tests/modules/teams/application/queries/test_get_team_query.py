from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.teams.application.queries.get_team_query import GetTeamQuery
from modules.teams.errors import TeamErrors


def test_returns_team_detail_from_query_repository():
    team_id = uuid4()
    expected = Mock()
    repository = Mock()
    repository.get.return_value = expected

    result = GetTeamQuery(repository).execute(team_id)

    assert result is expected
    repository.get.assert_called_once_with(team_id)


def test_raises_not_found_when_team_does_not_exist():
    repository = Mock()
    repository.get.return_value = None

    with pytest.raises(type(TeamErrors.NotFound)) as error:
        GetTeamQuery(repository).execute(uuid4())

    assert error.value is TeamErrors.NotFound
