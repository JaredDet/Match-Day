from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.news.application.commands.delete_news_use_case import DeleteNewsUseCase
from modules.news.domain.news import News
from modules.news.errors import NewsErrors

pytestmark = pytest.mark.django_db


def test_deletes_news():
    news_repository = Mock()

    news = News.create(
        title="Noticia",
        content={"blocks": []},
    )
    news_repository.get_for_update.return_value = news

    use_case = DeleteNewsUseCase(news_repository)

    use_case.execute(news_id=news.id)

    news_repository.get_for_update.assert_called_once_with(news.id)
    news_repository.delete.assert_called_once_with(news)


def test_rejects_deletion_of_nonexistent_news():
    news_repository = Mock()
    news_repository.get_for_update.return_value = None

    use_case = DeleteNewsUseCase(news_repository)

    news_id = uuid4()

    with pytest.raises(type(NewsErrors.NotFound)):
        use_case.execute(news_id=news_id)

    news_repository.get_for_update.assert_called_once_with(news_id)
    news_repository.delete.assert_not_called()
