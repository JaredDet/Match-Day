from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.group_repository import GroupRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class DeleteGroupUseCase:
    @inject
    def __init__(
        self, group_repository: GroupRepository, structure_repository: StructureRepository
    ):
        self.group_repository = group_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, group_id: UUID) -> None:
        entity = self.group_repository.get(group_id)

        if entity is None:
            raise TournamentErrors.GroupNotFound

        phase = self.structure_repository.lock_phase(entity.phase_id)
        entity = self.group_repository.get_for_update(group_id)

        if phase is None or entity is None:
            raise TournamentErrors.GroupNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        if self.structure_repository.group_has_dependencies(entity.id):
            raise TournamentErrors.HasDependencies

        self.structure_repository.delete(entity)
