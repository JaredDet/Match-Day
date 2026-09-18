from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.news.application.queries.get_news_query import GetNewsQuery
from modules.news.errors import NewsErrors


def test_returns_news_detail_from_query_repository():
    news_id = uuid4()
    expected = Mock()
    repository = Mock()
    repository.get.return_value = expected

    result = GetNewsQuery(repository).execute(news_id)

    assert result is expected
    repository.get.assert_called_once_with(news_id)


def test_raises_not_found_when_news_does_not_exist():
    repository = Mock()
    repository.get.return_value = None

    with pytest.raises(type(NewsErrors.NotFound)) as error:
        GetNewsQuery(repository).execute(uuid4())

    assert error.value is NewsErrors.NotFound
