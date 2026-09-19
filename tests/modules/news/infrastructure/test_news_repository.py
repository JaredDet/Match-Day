from datetime import UTC, datetime, timedelta

import pytest

from modules.news.domain.news import News, NewsStatus
from modules.news.infrastructure.repository.news_repository import NewsRepository


@pytest.fixture
def repository():
    return NewsRepository()


def create_news(
    *,
    title: str,
    status: NewsStatus = NewsStatus.DRAFT,
    scheduled_at: datetime | None = None,
) -> News:
    news = News.create(
        title=title,
        content={"children": ["Contenido de prueba"]},
    )
    news.status = status
    news.scheduled_at = scheduled_at
    news.save()
    return news


@pytest.mark.django_db
def test_get_next_scheduled_returns_none_when_there_are_no_scheduled_news(
    repository,
):
    result = repository.get_next_scheduled()

    assert result is None


@pytest.mark.django_db
def test_get_next_scheduled_returns_scheduled_news(
    repository,
):
    scheduled_at = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    news = create_news(
        title="Noticia programada",
        status=NewsStatus.SCHEDULED,
        scheduled_at=scheduled_at,
    )

    result = repository.get_next_scheduled()

    assert result.id == news.id


@pytest.mark.django_db
def test_get_next_scheduled_returns_earliest_scheduled_news(
    repository,
):
    first_scheduled_at = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)
    second_scheduled_at = first_scheduled_at + timedelta(hours=2)

    first_news = create_news(
        title="Primera noticia",
        status=NewsStatus.SCHEDULED,
        scheduled_at=first_scheduled_at,
    )

    create_news(
        title="Segunda noticia",
        status=NewsStatus.SCHEDULED,
        scheduled_at=second_scheduled_at,
    )

    result = repository.get_next_scheduled()

    assert result.id == first_news.id


@pytest.mark.django_db
def test_get_next_scheduled_ignores_news_that_are_not_scheduled(
    repository,
):
    scheduled_at = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    create_news(
        title="Borrador",
        status=NewsStatus.DRAFT,
        scheduled_at=scheduled_at,
    )

    create_news(
        title="Publicada",
        status=NewsStatus.PUBLISHED,
        scheduled_at=scheduled_at,
    )

    result = repository.get_next_scheduled()

    assert result is None


@pytest.mark.django_db
def test_list_scheduled_due_returns_past_scheduled_news(
    repository,
):
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    news = create_news(
        title="Noticia vencida",
        status=NewsStatus.SCHEDULED,
        scheduled_at=now - timedelta(minutes=10),
    )

    result = repository.list_scheduled_due(now)

    assert [item.id for item in result] == [news.id]


@pytest.mark.django_db
def test_list_scheduled_due_includes_news_scheduled_at_now(
    repository,
):
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    news = create_news(
        title="Noticia ahora",
        status=NewsStatus.SCHEDULED,
        scheduled_at=now,
    )

    result = repository.list_scheduled_due(now)

    assert [item.id for item in result] == [news.id]


@pytest.mark.django_db
def test_list_scheduled_due_ignores_future_and_non_scheduled_news(
    repository,
):
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    due_news = create_news(
        title="Noticia vencida",
        status=NewsStatus.SCHEDULED,
        scheduled_at=now - timedelta(minutes=10),
    )

    create_news(
        title="Noticia futura",
        status=NewsStatus.SCHEDULED,
        scheduled_at=now + timedelta(minutes=10),
    )

    create_news(
        title="Borrador",
        status=NewsStatus.DRAFT,
        scheduled_at=now - timedelta(minutes=10),
    )

    create_news(
        title="Publicada",
        status=NewsStatus.PUBLISHED,
        scheduled_at=now - timedelta(minutes=10),
    )

    result = repository.list_scheduled_due(now)

    assert [item.id for item in result] == [due_news.id]
