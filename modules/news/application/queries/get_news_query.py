from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from modules.news.domain.news import NewsStatus
from modules.news.errors import NewsErrors
from modules.news.infrastructure.query_repository.news_query_repository import (
    NewsQueryRepository,
)


@dataclass(frozen=True, slots=True)
class NewsDetail:
    id: UUID
    title: str
    team_id: UUID | None
    cover_image: str | None
    content: dict
    status: NewsStatus
    scheduled_at: datetime | None
    published_at: datetime | None


class GetNewsQuery:
    @inject
    def __init__(self, news_query_repository: NewsQueryRepository):
        self.news_query_repository = news_query_repository

    def execute(self, news_id: UUID) -> NewsDetail:
        news = self.news_query_repository.get(news_id)

        if news is None:
            raise NewsErrors.NotFound

        return news
