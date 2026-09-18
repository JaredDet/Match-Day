import injector

from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.application.commands.delete_news_use_case import DeleteNewsUseCase
from modules.news.application.commands.publish_news_use_case import PublishNewsUseCase
from modules.news.application.commands.schedule_news_use_case import ScheduleNewsUseCase
from modules.news.application.commands.unschedule_news_use_case import UnscheduleNewsUseCase
from modules.news.application.commands.update_news_use_case import UpdateNewsUseCase
from modules.news.application.news_content_parser import NewsContentParser
from modules.news.application.queries.get_news_query import GetNewsQuery
from modules.news.application.queries.list_news_query import ListNewsQuery
from modules.news.infrastructure.query_repository.news_query_repository import (
    NewsQueryRepository,
)
from modules.news.infrastructure.repository.news_repository import NewsRepository


class NewsModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(NewsRepository, to=NewsRepository, scope=injector.singleton)
        binder.bind(NewsQueryRepository, to=NewsQueryRepository, scope=injector.singleton)
        binder.bind(CreateNewsUseCase, to=CreateNewsUseCase, scope=injector.singleton)
        binder.bind(UpdateNewsUseCase, to=UpdateNewsUseCase, scope=injector.singleton)
        binder.bind(ScheduleNewsUseCase, to=ScheduleNewsUseCase, scope=injector.singleton)
        binder.bind(UnscheduleNewsUseCase, to=UnscheduleNewsUseCase, scope=injector.singleton)
        binder.bind(PublishNewsUseCase, to=PublishNewsUseCase, scope=injector.singleton)
        binder.bind(DeleteNewsUseCase, to=DeleteNewsUseCase, scope=injector.singleton)
        binder.bind(GetNewsQuery, to=GetNewsQuery, scope=injector.singleton)
        binder.bind(ListNewsQuery, to=ListNewsQuery, scope=injector.singleton)
        binder.bind(NewsContentParser, to=NewsContentParser, scope=injector.singleton)
