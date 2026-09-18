import injector

from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.infrastructure.repository.news_repository import NewsRepository


class NewsModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(NewsRepository, to=NewsRepository, scope=injector.singleton)
        binder.bind(CreateNewsUseCase, to=CreateNewsUseCase, scope=injector.singleton)
