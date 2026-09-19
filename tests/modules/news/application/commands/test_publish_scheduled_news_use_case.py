from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

from modules.news.application.commands.publish_scheduled_news_use_case import (
    PublishScheduledNewsUseCase,
)
from modules.news.domain.news import News, NewsStatus


@pytest.fixture
def news_repository():
    return Mock()


@pytest.fixture
def use_case(news_repository):
    return PublishScheduledNewsUseCase(news_repository)


def create_news(
    *,
    status: NewsStatus = NewsStatus.SCHEDULED,
    scheduled_at: datetime | None = None,
) -> News:
    news = News.create(
        title="Noticia de prueba",
        content={"children": ["Contenido"]},
    )
    news.status = status
    news.scheduled_at = scheduled_at
    return news


@pytest.mark.django_db
def test_publish_all_scheduled_news_due(
    use_case,
    news_repository,
):
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    due_news = [
        create_news(scheduled_at=now - timedelta(minutes=10)),
        create_news(scheduled_at=now),
        create_news(scheduled_at=now - timedelta(hours=1)),
    ]

    news_repository.list_scheduled_due.return_value = due_news

    result = use_case.execute()

    assert result == 3

    for news in due_news:
        assert news.status == NewsStatus.PUBLISHED
        assert news.published_at is not None
        assert news.scheduled_at is None

    assert news_repository.save.call_count == 3


@pytest.mark.django_db
def test_publish_scheduled_news_uses_current_time(
    use_case,
    news_repository,
):
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    news = create_news(
        scheduled_at=now - timedelta(minutes=5),
    )

    news_repository.list_scheduled_due.return_value = [news]

    use_case.execute()

    news_repository.list_scheduled_due.assert_called_once()

    queried_at = news_repository.list_scheduled_due.call_args.args[0]

    assert queried_at.tzinfo is not None


@pytest.mark.django_db
def test_publish_all_due_news_with_same_publication_time(
    use_case,
    news_repository,
):
    news = [
        create_news(),
        create_news(),
        create_news(),
    ]

    news_repository.list_scheduled_due.return_value = news

    use_case.execute()

    published_at = news[0].published_at

    assert published_at is not None

    for item in news:
        assert item.published_at == published_at


@pytest.mark.django_db
def test_returns_zero_when_there_are_no_due_news(
    use_case,
    news_repository,
):
    news_repository.list_scheduled_due.return_value = []

    result = use_case.execute()

    assert result == 0
    news_repository.save.assert_not_called()


@pytest.mark.django_db
def test_publishes_news_through_domain_method(
    use_case,
    news_repository,
):
    news = Mock(spec=News)
    news_repository.list_scheduled_due.return_value = [news]

    result = use_case.execute()

    assert result == 1
    news.publish.assert_called_once()

    published_at = news.publish.call_args.args[0]
    assert published_at.tzinfo is not None

    news_repository.save.assert_called_once_with(news)
