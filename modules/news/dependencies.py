import injector

from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.application.commands.publish_news_use_case import PublishNewsUseCase
from modules.news.application.commands.unschedule_news_use_case import UnscheduleNewsUseCase
from modules.news.infrastructure.repository.news_repository import NewsRepository


class NewsModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(NewsRepository, to=NewsRepository, scope=injector.singleton)
        binder.bind(CreateNewsUseCase, to=CreateNewsUseCase, scope=injector.singleton)
        binder.bind(PublishNewsUseCase, to=PublishNewsUseCase, scope=injector.singleton)
        binder.bind(UnscheduleNewsUseCase, to=UnscheduleNewsUseCase, scope=injector.singleton)
