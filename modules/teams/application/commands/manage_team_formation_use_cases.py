from django.db import transaction
from injector import inject

from modules.teams.domain.formation import TeamFormation
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.formation_repository import FormationRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class CreateTeamFormationUseCase:
    @inject
    def __init__(self, teams: TeamRepository, formations: FormationRepository):
        self.teams, self.formations = teams, formations

    @transaction.atomic
    def execute(self, *, team_id, **data):
        team = self.teams.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound
        formation = TeamFormation.create(team=team, **data)
        self.formations.save(formation)
        return formation.id


class UpdateTeamFormationUseCase:
    @inject
    def __init__(self, formations: FormationRepository):
        self.formations = formations

    @transaction.atomic
    def execute(self, *, team_id, formation_id, **data):
        formation = self.formations.get_for_update(formation_id, team_id)
        if formation is None:
            raise TeamErrors.FormationNotFound
        formation.update(**data)
        self.formations.save(formation)


class DeleteTeamFormationUseCase:
    @inject
    def __init__(self, formations: FormationRepository):
        self.formations = formations

    @transaction.atomic
    def execute(self, *, team_id, formation_id):
        formation = self.formations.get_for_update(formation_id, team_id)
        if formation is None:
            raise TeamErrors.FormationNotFound
        self.formations.delete(formation)
