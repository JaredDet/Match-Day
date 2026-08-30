from unittest.mock import Mock

from modules.teams.application.queries.list_teams_query import ListTeamsQuery


def test_returns_team_summaries_from_query_repository():
    expected = (Mock(), Mock())
    repository = Mock()
    repository.list.return_value = expected
    query = ListTeamsQuery(repository)

    result = query.execute(search="atlético")

    assert result is expected
    repository.list.assert_called_once_with(search="atlético")
