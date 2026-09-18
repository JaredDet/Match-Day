from uuid import UUID

from modules.news.domain.news import News


class NewsRepository:
    def get(self, news_id: UUID) -> News | None:
        return News.objects.filter(id=news_id).first()

    def get_for_update(self, news_id: UUID) -> News | None:
        return News.objects.select_for_update().filter(id=news_id).first()

    def save(self, news: News) -> None:
        news.save()

    def delete(self, news: News) -> None:
        news.delete()
