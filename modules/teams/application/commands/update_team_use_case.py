from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class UpdateTeamUseCase:
    @inject
    def __init__(self, team_repository: TeamRepository):
        self.team_repository = team_repository

    @transaction.atomic
    def execute(self, *, team_id: UUID, name: str) -> None:
        team = self.team_repository.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound

        team.rename(name)
        if self.team_repository.exists_other_by_name(team.name, team.id):
            raise TeamErrors.AlreadyExists
        self.team_repository.save(team)
