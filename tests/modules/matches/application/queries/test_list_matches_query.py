from datetime import date
from unittest.mock import Mock

from modules.matches.application.queries.list_matches_query import ListMatchesQuery
from modules.matches.domain.match import MatchStatus


def test_returns_summaries_from_query_repository():
    expected = (Mock(), Mock())
    repository = Mock()
    repository.list.return_value = expected
    query = ListMatchesQuery(repository)
    match_date = date(2026, 8, 30)

    result = query.execute(status=MatchStatus.LIVE, date=match_date)

    assert result is expected
    repository.list.assert_called_once_with(status=MatchStatus.LIVE, date=match_date)
