from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.news.application.commands.update_news_use_case import UpdateNewsUseCase
from modules.news.domain.news import News, NewsStatus
from modules.news.errors import NewsErrors

pytestmark = pytest.mark.django_db


def test_updates_and_persists_news():
    news_repository = Mock()
    news_content_parser = Mock()

    content = {"children": ["Contenido nuevo"]}
    news_content_parser.parse.return_value = content

    news = News.create(
        title="Título anterior",
        content={"children": ["Contenido anterior"]},
    )
    news_repository.get_for_update.return_value = news

    use_case = UpdateNewsUseCase(
        news_repository,
        news_content_parser,
    )

    use_case.execute(
        news_id=news.id,
        title="  Título   nuevo  ",
        content=content,
        preview="Resumen corto",
        cover_image="news/covers/new-cover.jpg",
    )

    assert news.title == "Título nuevo"
    assert news.content == content
    assert news.preview == "Resumen corto"
    assert news.cover_image == "news/covers/new-cover.jpg"
    assert news.status == NewsStatus.DRAFT

    news_repository.get_for_update.assert_called_once_with(news.id)
    news_content_parser.parse.assert_called_once_with(content)
    news_repository.save.assert_called_once_with(news)


def test_rejects_update_of_nonexistent_news():
    news_repository = Mock()
    news_content_parser = Mock()
    news_repository.get_for_update.return_value = None

    use_case = UpdateNewsUseCase(
        news_repository,
        news_content_parser,
    )

    news_id = uuid4()
    content = {"children": ["Contenido nuevo"]}

    with pytest.raises(type(NewsErrors.NotFound)):
        use_case.execute(
            news_id=news_id,
            title="Título nuevo",
            content=content,
            cover_image=None,
        )

    news_repository.get_for_update.assert_called_once_with(news_id)
    news_content_parser.parse.assert_not_called()
    news_repository.save.assert_not_called()
