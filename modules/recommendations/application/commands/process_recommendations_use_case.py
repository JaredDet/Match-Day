from django.utils import timezone
from injector import inject

from modules.recommendations.application.commands.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from modules.recommendations.application.commands.purge_navigation_history_use_case import (
    PurgeNavigationHistoryUseCase,
)
from modules.recommendations.constants import WORKER_BATCH_SIZE
from modules.recommendations.infrastructure.repository.navigation_repository import (
    NavigationRepository,
)


class ProcessRecommendationsUseCase:
    @inject
    def __init__(
        self,
        navigation_repository: NavigationRepository,
        generate: GenerateRecommendationsUseCase,
        purge: PurgeNavigationHistoryUseCase,
    ):
        self.navigation_repository = navigation_repository
        self.generate = generate
        self.purge = purge

    def execute(self, *, batch_size=WORKER_BATCH_SIZE, now=None):
        if not 1 <= batch_size <= 1000:
            raise ValueError("batch_size must be between 1 and 1000")
        now = now or timezone.now()
        self.purge.execute(now=now)
        self.generate.execute(now=now)
        return sum(
            self.generate.execute(visitor_id=visitor_id, now=now)
            for visitor_id in self.navigation_repository.due_visitors(now, batch_size)
        )
