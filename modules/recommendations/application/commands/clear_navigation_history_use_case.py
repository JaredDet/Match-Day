from django.db import transaction
from injector import inject

from modules.recommendations.infrastructure.repository.navigation_repository import (
    NavigationRepository,
)


class ClearNavigationHistoryUseCase:
    @inject
    def __init__(self, navigation_repository: NavigationRepository):
        self.navigation_repository = navigation_repository

    @transaction.atomic
    def execute(self, *, visitor_id):
        visitor = self.navigation_repository.lock_visitor(visitor_id)
        if visitor is not None:
            self.navigation_repository.delete_visitor(visitor)
