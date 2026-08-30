from datetime import datetime
from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import Match
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class CreateMatchUseCase:
    @inject
    def __init__(self, match_repository: MatchRepository, team_repository: TeamRepository):
        self.match_repository = match_repository
        self.team_repository = team_repository

    @transaction.atomic
    def execute(
        self,
        *,
        home_team_id: UUID,
        away_team_id: UUID,
        scheduled_at: datetime,
        stadium_name: str | None = None,
        referee_name: str | None = None,
    ) -> UUID:
        home_team = self.team_repository.get(home_team_id)
        away_team = self.team_repository.get(away_team_id)
        if home_team is None or away_team is None:
            raise TeamErrors.NotFound
        match = Match.schedule(
            home_team=home_team,
            away_team=away_team,
            scheduled_at=scheduled_at,
            stadium_name=stadium_name,
            referee_name=referee_name,
        )
        if self.match_repository.exists_fixture(match.fixture_key):
            raise MatchErrors.AlreadyExists
        self.match_repository.save(match)
        return match.id
