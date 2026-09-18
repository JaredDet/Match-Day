from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from modules.news.domain.news import News, NewsStatus

if TYPE_CHECKING:
    from modules.news.application.queries.list_news_query import NewsListItem


class NewsQueryRepository:
    def list(
        self,
        *,
        status: NewsStatus | None = None,
        team_id: UUID | None = None,
        published_from: datetime | None = None,
        published_to: datetime | None = None,
    ) -> tuple[NewsListItem, ...]:
        from modules.news.application.queries.list_news_query import NewsListItem

        queryset = News.objects.all()

        if status is not None:
            queryset = queryset.filter(status=status)

        if team_id is not None:
            queryset = queryset.filter(team_id=team_id)

        if published_from is not None:
            queryset = queryset.filter(published_at__gte=published_from)

        if published_to is not None:
            queryset = queryset.filter(published_at__lte=published_to)

        rows = queryset.order_by("-published_at", "-id").values(
            "id",
            "title",
            "team_id",
            "cover_image",
            "content",
            "status",
            "scheduled_at",
            "published_at",
        )

        return tuple(
            NewsListItem(
                id=row["id"],
                title=row["title"],
                team_id=row["team_id"],
                cover_image=row["cover_image"] or None,
                content=row["content"],
                status=NewsStatus(row["status"]),
                scheduled_at=row["scheduled_at"],
                published_at=row["published_at"],
            )
            for row in rows
        )
