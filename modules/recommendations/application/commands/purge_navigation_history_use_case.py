from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.recommendations.infrastructure.repository.navigation_repository import (
    NavigationRepository,
)


class PurgeNavigationHistoryUseCase:
    @inject
    def __init__(self, navigation_repository: NavigationRepository):
        self.navigation_repository = navigation_repository

    @transaction.atomic
    def execute(self, *, now=None):
        return self.navigation_repository.purge(now or timezone.now())
