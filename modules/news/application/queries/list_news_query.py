from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from modules.news.domain.news import NewsStatus
from modules.news.infrastructure.query_repository.news_query_repository import (
    NewsQueryRepository,
)


@dataclass(frozen=True, slots=True)
class NewsListItem:
    id: UUID
    title: str
    team_id: UUID | None
    cover_image: str | None
    preview: str
    status: NewsStatus
    scheduled_at: datetime | None
    published_at: datetime | None


class ListNewsQuery:
    @inject
    def __init__(self, news_query_repository: NewsQueryRepository):
        self.news_query_repository = news_query_repository

    def execute(
        self,
        *,
        status: NewsStatus | None = None,
        team_id: UUID | None = None,
        published_from: datetime | None = None,
        published_to: datetime | None = None,
    ) -> tuple[NewsListItem, ...]:
        return self.news_query_repository.list(
            status=status,
            team_id=team_id,
            published_from=published_from,
            published_to=published_to,
        )
