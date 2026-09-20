from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.team_repository import TeamRepository
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class AddSeasonTeamUseCase:
    @inject
    def __init__(self, structure_repository: StructureRepository, team_repository: TeamRepository):
        self.structure_repository = structure_repository
        self.team_repository = team_repository

    @transaction.atomic
    def execute(self, *, season_id: UUID, team_id: UUID) -> None:
        season = self.structure_repository.lock_season(season_id)

        if season is None:
            raise TournamentErrors.SeasonNotFound

        if self.structure_repository.season_has_generated_phases(season_id):
            raise TournamentErrors.StructureLocked

        if self.team_repository.get(team_id) is None:
            raise TeamErrors.NotFound

        self.structure_repository.add_team(season, team_id)
