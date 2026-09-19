import logging
import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.dependency_injector import injector_instance
from modules.news.application.commands.publish_scheduled_news_use_case import (
    PublishScheduledNewsUseCase,
)
from modules.news.infrastructure.repository.news_repository import NewsRepository

DAILY_INTERVAL_SECONDS = 24 * 60 * 60
ACTIVE_INTERVAL_SECONDS = 5 * 60
ACTIVATION_WINDOW = timedelta(hours=24)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Publica automáticamente las noticias programadas"

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true")

    def handle(self, *args, **options):
        publish_use_case = injector_instance.get(PublishScheduledNewsUseCase)
        news_repository = injector_instance.get(NewsRepository)

        self.stdout.write("Monitor de noticias programadas activo")

        try:
            while True:
                try:
                    published = publish_use_case.execute()

                    if published:
                        self.stdout.write(f"Noticias publicadas automáticamente: {published}")

                    interval = self._get_next_interval(news_repository)

                except Exception:
                    if options["once"]:
                        raise

                    logger.exception("Falló la publicación de noticias programadas")
                    interval = ACTIVE_INTERVAL_SECONDS

                if options["once"]:
                    return

                self.stdout.write(f"Próxima revisión en {interval // 60} minutos")
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write("Monitor de noticias detenido")

    @staticmethod
    def _get_next_interval(news_repository: NewsRepository) -> int:
        next_news = news_repository.get_next_scheduled()

        if next_news is None:
            return DAILY_INTERVAL_SECONDS

        now = timezone.now()
        time_until_publication = next_news.scheduled_at - now

        if time_until_publication <= ACTIVATION_WINDOW:
            return ACTIVE_INTERVAL_SECONDS

        return DAILY_INTERVAL_SECONDS
