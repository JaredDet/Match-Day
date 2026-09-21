import logging
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import close_old_connections

from core.dependency_injector import injector_instance
from modules.recommendations.application.commands.process_recommendations_use_case import (
    ProcessRecommendationsUseCase,
)
from modules.recommendations.constants import WORKER_BATCH_SIZE, WORKER_INTERVAL_SECONDS

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Calcula recomendaciones desde la actividad de navegacion"

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true")
        parser.add_argument("--interval", type=int, default=WORKER_INTERVAL_SECONDS)
        parser.add_argument("--batch-size", type=int, default=WORKER_BATCH_SIZE)

    def handle(self, *args, **options):
        if options["interval"] < 1 or not 1 <= options["batch_size"] <= 1000:
            raise CommandError("interval >= 1; batch-size between 1 and 1000")
        process = injector_instance.get(ProcessRecommendationsUseCase)
        try:
            while True:
                close_old_connections()
                try:
                    count = process.execute(batch_size=options["batch_size"])
                    self.stdout.write(f"Perfiles actualizados: {count}")
                except Exception:
                    if options["once"]:
                        raise
                    logger.exception("Recommendation processing failed")
                finally:
                    close_old_connections()
                if options["once"]:
                    return
                time.sleep(options["interval"])
        except KeyboardInterrupt:
            self.stdout.write("Monitor de recomendaciones detenido")
