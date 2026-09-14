import logging
import time

from django.core.management.base import BaseCommand

from core.dependency_injector import injector_instance
from modules.matches.application.commands.synchronize_match_clocks_use_case import (
    SynchronizeMatchClocksUseCase,
)

DEFAULT_INTERVAL_SECONDS = 30
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sincroniza los relojes activos y publica snapshots y alertas por WebSocket"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=DEFAULT_INTERVAL_SECONDS,
            help="Segundos entre sincronizaciones (por defecto: 30)",
        )
        parser.add_argument("--once", action="store_true")

    def handle(self, *args, **options):
        interval = options["interval"]
        if interval <= 0:
            raise ValueError("El intervalo debe ser mayor que cero")

        use_case = injector_instance.get(SynchronizeMatchClocksUseCase)
        self.stdout.write(f"Monitor de reloj activo; intervalo={interval}s")

        try:
            while True:
                try:
                    synchronized = use_case.execute()
                    self.stdout.write(f"Relojes sincronizados: {synchronized}")
                except Exception:
                    if options["once"]:
                        raise
                    logger.exception("Falló la sincronización de los relojes")

                if options["once"]:
                    return

                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write("Monitor de reloj detenido")
