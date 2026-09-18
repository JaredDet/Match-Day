from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.news.application.commands.schedule_news_use_case import ScheduleNewsUseCase
from modules.news.domain.news import News, NewsStatus
from modules.news.errors import NewsErrors

pytestmark = pytest.mark.django_db


def test_schedules_and_persists_news():
    news_repository = Mock()

    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    news_repository.get_for_update.return_value = news

    use_case = ScheduleNewsUseCase(news_repository)

    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)

    use_case.execute(
        news_id=news.id,
        scheduled_at=scheduled_at,
    )

    assert news.status == NewsStatus.SCHEDULED
    assert news.scheduled_at == scheduled_at

    news_repository.get_for_update.assert_called_once_with(news.id)
    news_repository.save.assert_called_once_with(news)


def test_rejects_scheduling_nonexistent_news():
    news_repository = Mock()
    news_repository.get_for_update.return_value = None

    use_case = ScheduleNewsUseCase(news_repository)

    news_id = uuid4()
    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)

    with pytest.raises(type(NewsErrors.NotFound)):
        use_case.execute(
            news_id=news_id,
            scheduled_at=scheduled_at,
        )

    news_repository.get_for_update.assert_called_once_with(news_id)
    news_repository.save.assert_not_called()
