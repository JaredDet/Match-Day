from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class CreateTeamUseCase:
    @inject
    def __init__(self, team_repository: TeamRepository):
        self.team_repository = team_repository

    @transaction.atomic
    def execute(self, *, name: str, head_coach_name: str | None = None) -> UUID:
        if not head_coach_name or not head_coach_name.strip():
            raise TeamErrors.InvalidHeadCoach

        team = Team.create(name=name, head_coach_name=head_coach_name)

        if self.team_repository.exists_by_name(team.name):
            raise TeamErrors.AlreadyExists

        self.team_repository.save(team)

        return team.id
