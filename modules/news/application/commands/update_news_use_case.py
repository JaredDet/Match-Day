from uuid import UUID

from django.db import transaction
from injector import inject

from modules.news.application.news_content_parser import NewsContentParser
from modules.news.errors import NewsErrors
from modules.news.infrastructure.repository.news_repository import NewsRepository

_UNSET = object()


class UpdateNewsUseCase:
    @inject
    def __init__(
        self,
        news_repository: NewsRepository,
        news_content_parser: NewsContentParser,
    ):
        self.news_repository = news_repository
        self.news_content_parser = news_content_parser

    @transaction.atomic
    def execute(
        self,
        *,
        news_id: UUID,
        title: str,
        content: dict,
        cover_image: str | None = _UNSET,
    ) -> None:
        news = self.news_repository.get_for_update(news_id)

        if news is None:
            raise NewsErrors.NotFound

        content = self.news_content_parser.parse(content)

        news.rename(title)
        news.update_content(content)

        if cover_image is not _UNSET:
            news.update_cover_image(cover_image)

        self.news_repository.save(news)
