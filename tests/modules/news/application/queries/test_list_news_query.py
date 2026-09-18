from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

from modules.news.application.queries.list_news_query import ListNewsQuery
from modules.news.domain.news import NewsStatus


def test_returns_news_from_query_repository():
    team_id = uuid4()
    published_from = datetime(2026, 8, 1, tzinfo=UTC)
    published_to = datetime(2026, 8, 31, tzinfo=UTC)
    expected = (Mock(), Mock())
    repository = Mock()
    repository.list.return_value = expected

    result = ListNewsQuery(repository).execute(
        status=NewsStatus.PUBLISHED,
        team_id=team_id,
        published_from=published_from,
        published_to=published_to,
    )

    assert result is expected
    repository.list.assert_called_once_with(
        status=NewsStatus.PUBLISHED,
        team_id=team_id,
        published_from=published_from,
        published_to=published_to,
    )


def test_returns_all_news_when_no_filters_are_provided():
    expected = (Mock(), Mock())
    repository = Mock()
    repository.list.return_value = expected

    result = ListNewsQuery(repository).execute()

    assert result is expected
    repository.list.assert_called_once_with(
        status=None,
        team_id=None,
        published_from=None,
        published_to=None,
    )
