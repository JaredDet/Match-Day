from unittest.mock import Mock
from uuid import uuid4

from modules.teams.application.queries.list_players_query import ListPlayersQuery


def test_returns_player_summaries_from_query_repository():
    team_id = uuid4()
    expected = (Mock(), Mock())
    repository = Mock()
    repository.list.return_value = expected

    result = ListPlayersQuery(repository).execute(search="mateo", team_id=team_id)

    assert result is expected
    repository.list.assert_called_once_with(search="mateo", team_id=team_id)
