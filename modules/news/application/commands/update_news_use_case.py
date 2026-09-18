from uuid import UUID

from django.db import transaction
from injector import inject

from modules.news.errors import NewsErrors
from modules.news.infrastructure.repository.news_repository import NewsRepository


class UpdateNewsUseCase:
    @inject
    def __init__(self, news_repository: NewsRepository):
        self.news_repository = news_repository

    @transaction.atomic
    def execute(
        self,
        *,
        news_id: UUID,
        title: str,
        content: dict,
        cover_image: str | None,
    ) -> None:
        news = self.news_repository.get_for_update(news_id)

        if news is None:
            raise NewsErrors.NotFound

        news.rename(title)
        news.update_content(content)
        news.update_cover_image(cover_image)

        self.news_repository.save(news)
