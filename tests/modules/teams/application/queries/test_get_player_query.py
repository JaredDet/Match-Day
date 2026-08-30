from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.teams.application.queries.get_player_query import GetPlayerQuery
from modules.teams.errors import TeamErrors


def test_returns_player_detail_from_query_repository():
    player_id = uuid4()
    expected = Mock()
    repository = Mock()
    repository.get.return_value = expected

    result = GetPlayerQuery(repository).execute(player_id)

    assert result is expected
    repository.get.assert_called_once_with(player_id)


def test_raises_not_found_when_player_does_not_exist():
    repository = Mock()
    repository.get.return_value = None

    with pytest.raises(type(TeamErrors.PlayerNotFound)) as error:
        GetPlayerQuery(repository).execute(uuid4())

    assert error.value is TeamErrors.PlayerNotFound
