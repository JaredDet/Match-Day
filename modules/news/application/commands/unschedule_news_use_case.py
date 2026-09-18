from uuid import UUID

from django.db import transaction
from injector import inject

from modules.news.errors import NewsErrors
from modules.news.infrastructure.repository.news_repository import NewsRepository


class UnscheduleNewsUseCase:
    @inject
    def __init__(self, news_repository: NewsRepository):
        self.news_repository = news_repository

    @transaction.atomic
    def execute(self, *, news_id: UUID) -> None:
        news = self.news_repository.get_for_update(news_id)
        if news is None:
            raise NewsErrors.NotFound

        news.unschedule()
        self.news_repository.save(news)
