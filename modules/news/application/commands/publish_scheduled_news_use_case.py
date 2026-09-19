from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.news.infrastructure.repository.news_repository import NewsRepository


class PublishScheduledNewsUseCase:
    @inject
    def __init__(self, news_repository: NewsRepository):
        self.news_repository = news_repository

    @transaction.atomic
    def execute(self) -> int:
        now = timezone.now()
        news = self.news_repository.list_scheduled_due(now)

        for item in news:
            item.publish(now)
            self.news_repository.save(item)

        return len(news)
