from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.domain.group import Group
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.group_repository import GroupRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class CreateGroupUseCase:
    @inject
    def __init__(
        self,
        group_repository: GroupRepository,
        structure_repository: StructureRepository,
    ):
        self.group_repository = group_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, phase_id: UUID, name: str) -> UUID:
        phase = self.structure_repository.lock_phase(phase_id)

        if phase is None:
            raise TournamentErrors.PhaseNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        group = Group.create(phase=phase, name=name)

        self.group_repository.save(group)

        return group.id
