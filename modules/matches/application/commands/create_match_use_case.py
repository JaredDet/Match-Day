from datetime import datetime
from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import Match
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class CreateMatchUseCase:
    @inject
    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    @transaction.atomic
    def execute(
        self,
        *,
        home_team_name: str,
        away_team_name: str,
        scheduled_at: datetime,
    ) -> UUID:
        match = Match.schedule(
            home_team_name=home_team_name,
            away_team_name=away_team_name,
            scheduled_at=scheduled_at,
        )
        if self.match_repository.exists_fixture(match.fixture_key):
            raise MatchErrors.AlreadyExists
        self.match_repository.save(match)
        return match.id
