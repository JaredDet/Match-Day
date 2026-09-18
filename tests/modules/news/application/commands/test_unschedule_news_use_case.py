from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.news.application.commands.unschedule_news_use_case import (
    UnscheduleNewsUseCase,
)
from modules.news.domain.news import News, NewsStatus
from modules.news.errors import NewsErrors

pytestmark = pytest.mark.django_db


def test_unschedules_news():
    repository = Mock()
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)
    news.schedule(scheduled_at)

    repository.get_for_update.return_value = news

    use_case = UnscheduleNewsUseCase(repository)

    use_case.execute(news_id=news.id)

    assert news.status == NewsStatus.DRAFT
    assert news.scheduled_at is None
    repository.get_for_update.assert_called_once_with(news.id)
    repository.save.assert_called_once_with(news)


def test_rejects_nonexistent_news():
    repository = Mock()
    repository.get_for_update.return_value = None

    use_case = UnscheduleNewsUseCase(repository)

    news_id = uuid4()

    with pytest.raises(type(NewsErrors.NotFound)):
        use_case.execute(news_id=news_id)

    repository.get_for_update.assert_called_once_with(news_id)
    repository.save.assert_not_called()
