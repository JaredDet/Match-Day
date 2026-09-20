from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.team_repository import TeamRepository
from modules.tournaments.domain.season import Season
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.season_repository import SeasonRepository
from modules.tournaments.infrastructure.repository.tournament_repository import TournamentRepository


class CreateSeasonUseCase:
    @inject
    def __init__(
        self,
        season_repository: SeasonRepository,
        tournament_repository: TournamentRepository,
        team_repository: TeamRepository,
    ):
        self.season_repository = season_repository
        self.tournament_repository = tournament_repository
        self.team_repository = team_repository

    @transaction.atomic
    def execute(
        self, *, tournament_id: UUID, name: str, team_ids: list[UUID] | None = None
    ) -> UUID:
        if self.tournament_repository.get_for_update(tournament_id) is None:
            raise TournamentErrors.NotFound

        for team_id in set(team_ids or []):
            if self.team_repository.get(team_id) is None:
                raise TeamErrors.NotFound

        season = Season.create(tournament_id=tournament_id, name=name)

        self.season_repository.save(season)
        self.season_repository.set_teams(season, team_ids or [])

        return season.id
