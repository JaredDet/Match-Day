from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.domain.news import News, NewsStatus
from modules.teams.errors import TeamErrors

pytestmark = pytest.mark.django_db


def test_creates_and_persists_news():
    news_repository = Mock()
    team_repository = Mock()
    news_content_parser = Mock()

    team_id = uuid4()
    content = {"children": ["Contenido de la noticia."]}

    team_repository.get_for_update.return_value = Mock()
    news_content_parser.parse.return_value = content

    use_case = CreateNewsUseCase(
        news_repository,
        team_repository,
        news_content_parser,
    )

    news_id = use_case.execute(
        title="  Nueva   noticia  ",
        content=content,
        team_id=team_id,
        cover_image="news/covers/cover.jpg",
    )

    news = news_repository.save.call_args.args[0]

    assert isinstance(news, News)
    assert news.id == news_id
    assert news.team_id == team_id
    assert news.title == "Nueva noticia"
    assert news.content == content
    assert news.cover_image == "news/covers/cover.jpg"
    assert news.status == NewsStatus.DRAFT

    team_repository.get_for_update.assert_called_once_with(team_id)
    news_content_parser.parse.assert_called_once_with(content)
    news_repository.save.assert_called_once_with(news)


def test_creates_general_news_without_team():
    news_repository = Mock()
    team_repository = Mock()
    news_content_parser = Mock()

    content = {"children": ["Noticia general."]}
    news_content_parser.parse.return_value = content

    use_case = CreateNewsUseCase(
        news_repository,
        team_repository,
        news_content_parser,
    )

    news_id = use_case.execute(
        title="  Noticia   general  ",
        content=content,
    )

    news = news_repository.save.call_args.args[0]

    assert isinstance(news, News)
    assert news.id == news_id
    assert news.team_id is None
    assert news.title == "Noticia general"
    assert news.content == content
    assert news.status == NewsStatus.DRAFT

    team_repository.get_for_update.assert_not_called()
    news_content_parser.parse.assert_called_once_with(content)
    news_repository.save.assert_called_once_with(news)


def test_rejects_news_with_nonexistent_team():
    news_repository = Mock()
    team_repository = Mock()
    news_content_parser = Mock()

    team_repository.get_for_update.return_value = None

    use_case = CreateNewsUseCase(
        news_repository,
        team_repository,
        news_content_parser,
    )

    team_id = uuid4()
    content = {"children": ["Nueva noticia."]}

    with pytest.raises(type(TeamErrors.NotFound)):
        use_case.execute(
            title="Nueva noticia",
            content=content,
            team_id=team_id,
        )

    team_repository.get_for_update.assert_called_once_with(team_id)
    news_content_parser.parse.assert_not_called()
    news_repository.save.assert_not_called()
