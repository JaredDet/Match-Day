from datetime import datetime
from uuid import UUID

from modules.news.domain.news import News, NewsStatus


class NewsRepository:
    def get(self, news_id: UUID) -> News | None:
        return News.objects.filter(id=news_id).first()

    def get_for_update(self, news_id: UUID) -> News | None:
        return News.objects.select_for_update().filter(id=news_id).first()

    def get_next_scheduled(self) -> News | None:
        return (
            News.objects.filter(
                status=NewsStatus.SCHEDULED,
            )
            .order_by("scheduled_at", "id")
            .first()
        )

    def list_scheduled_due(self, now: datetime) -> list[News]:
        return list(
            News.objects.select_for_update().filter(
                status=NewsStatus.SCHEDULED,
                scheduled_at__lte=now,
            )
        )

    def save(self, news: News) -> None:
        news.save()

    def delete(self, news: News) -> None:
        news.delete()
