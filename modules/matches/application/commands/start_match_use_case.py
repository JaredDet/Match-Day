from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class StartMatchUseCase:
    @inject
    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    @transaction.atomic
    def execute(self, match_id: UUID) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        match.start()
        self.match_repository.save(match)
