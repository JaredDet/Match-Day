from datetime import UTC, datetime

import pytest

from modules.news.domain.news import News, NewsStatus
from modules.news.errors import NewsErrors


def test_creates_news_as_draft():
    news = News.create(
        title="  Nueva   noticia  ",
        content={"blocks": []},
    )

    assert news.title == "Nueva noticia"
    assert news.status == NewsStatus.DRAFT


def test_renames_news_with_normalized_title():
    news = News.create(
        title="Título anterior",
        content={"blocks": []},
    )

    news.rename("  Título   nuevo ")

    assert news.title == "Título nuevo"


def test_updates_news_content():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    content = {"blocks": [{"type": "paragraph", "text": "Contenido"}]}

    news.update_content(content)

    assert news.content == content


def test_updates_news_cover_image():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )

    news.update_cover_image("news/covers/cover.jpg")

    assert news.cover_image == "news/covers/cover.jpg"


def test_schedules_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)

    news.schedule(scheduled_at)

    assert news.status == NewsStatus.SCHEDULED
    assert news.scheduled_at == scheduled_at


def test_unschedules_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)
    news.schedule(scheduled_at)

    news.unschedule()

    assert news.status == NewsStatus.DRAFT
    assert news.scheduled_at is None


def test_publishes_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    published_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)

    news.publish(published_at)

    assert news.status == NewsStatus.PUBLISHED
    assert news.published_at == published_at
    assert news.scheduled_at is None


def test_publishes_scheduled_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)
    published_at = datetime(2026, 9, 20, 16, 0, tzinfo=UTC)

    news.schedule(scheduled_at)
    news.publish(published_at)

    assert news.status == NewsStatus.PUBLISHED
    assert news.published_at == published_at
    assert news.scheduled_at is None


def test_cannot_schedule_published_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    news.publish(datetime(2026, 9, 20, 15, 0, tzinfo=UTC))

    with pytest.raises(type(NewsErrors.CannotSchedule)):
        news.schedule(datetime(2026, 9, 20, 16, 0, tzinfo=UTC))


def test_cannot_unschedule_draft_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )

    with pytest.raises(type(NewsErrors.NotScheduled)):
        news.unschedule()


def test_cannot_publish_published_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    news.publish(datetime(2026, 9, 20, 15, 0, tzinfo=UTC))

    with pytest.raises(type(NewsErrors.AlreadyPublished)):
        news.publish(datetime(2026, 9, 20, 16, 0, tzinfo=UTC))


def test_cannot_rename_published_news():
    news = News.create(
        title="Título original",
        content={"blocks": []},
    )
    news.publish(datetime(2026, 9, 20, 15, 0, tzinfo=UTC))

    with pytest.raises(type(NewsErrors.AlreadyPublished)):
        news.rename("Título nuevo")


def test_cannot_update_content_of_published_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    news.publish(datetime(2026, 9, 20, 15, 0, tzinfo=UTC))

    with pytest.raises(type(NewsErrors.AlreadyPublished)):
        news.update_content({"blocks": []})


def test_cannot_update_cover_image_of_published_news():
    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    news.publish(datetime(2026, 9, 20, 15, 0, tzinfo=UTC))

    with pytest.raises(type(NewsErrors.AlreadyPublished)):
        news.update_cover_image("news/covers/new-cover.jpg")


@pytest.mark.parametrize("title", ["", "   ", None])
def test_rejects_invalid_news_title(title):
    with pytest.raises(type(NewsErrors.InvalidTitle)):
        News.create(
            title=title,
            content={"blocks": []},
        )
