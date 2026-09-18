from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.news.application.commands.publish_news_use_case import PublishNewsUseCase
from modules.news.domain.news import News, NewsStatus
from modules.news.errors import NewsErrors

pytestmark = pytest.mark.django_db


def test_publishes_news():
    repository = Mock()
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    repository.get_for_update.return_value = news

    use_case = PublishNewsUseCase(repository)

    published_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)

    use_case.execute(
        news_id=news.id,
        published_at=published_at,
    )

    assert news.status == NewsStatus.PUBLISHED
    assert news.published_at == published_at
    assert news.scheduled_at is None
    repository.get_for_update.assert_called_once_with(news.id)
    repository.save.assert_called_once_with(news)


def test_rejects_nonexistent_news():
    repository = Mock()
    repository.get_for_update.return_value = None

    use_case = PublishNewsUseCase(repository)

    news_id = uuid4()

    with pytest.raises(type(NewsErrors.NotFound)):
        use_case.execute(news_id=news_id)

    repository.get_for_update.assert_called_once_with(news_id)
    repository.save.assert_not_called()
