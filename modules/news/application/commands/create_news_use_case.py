from uuid import UUID

from django.db import transaction
from injector import inject

from modules.news.domain.news import News
from modules.news.infrastructure.repository.news_repository import NewsRepository
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class CreateNewsUseCase:
    @inject
    def __init__(
        self,
        news_repository: NewsRepository,
        team_repository: TeamRepository,
    ):
        self.news_repository = news_repository
        self.team_repository = team_repository

    @transaction.atomic
    def execute(
        self,
        *,
        title: str,
        content: dict,
        team_id: UUID | None = None,
        cover_image: str | None = None,
    ) -> UUID:
        if team_id is not None and self.team_repository.get_for_update(team_id) is None:
            raise TeamErrors.NotFound

        news = News.create(
            team_id=team_id,
            title=title,
            cover_image=cover_image,
            content=content,
        )
        self.news_repository.save(news)
        return news.id
