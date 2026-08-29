import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.match_detail import MatchDetail
from modules.matches.errors import MatchErrors


def test_returns_match_detail_from_query_repository():
    expected = Mock(spec=MatchDetail)
    repository = Mock()
    repository.get.return_value = expected
    query = GetMatchQuery(repository)
    match_id = uuid.uuid4()

    result = query.execute(match_id)

    assert result is expected
    repository.get.assert_called_once_with(match_id)


def test_raises_not_found_when_match_does_not_exist():
    repository = Mock()
    repository.get.return_value = None
    query = GetMatchQuery(repository)

    with pytest.raises(type(MatchErrors.NotFound)) as exc_info:
        query.execute(uuid.uuid4())

    assert exc_info.value.code == "match_not_found"
