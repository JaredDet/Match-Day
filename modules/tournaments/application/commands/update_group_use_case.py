from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.domain.group import Group
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.group_repository import GroupRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class UpdateGroupUseCase:
    @inject
    def __init__(
        self, group_repository: GroupRepository, structure_repository: StructureRepository
    ):
        self.group_repository = group_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, group_id: UUID, name: str) -> None:
        group = self.group_repository.get(group_id)

        if group is None:
            raise TournamentErrors.GroupNotFound

        phase = self.structure_repository.lock_phase(group.phase_id)
        group = self.group_repository.get_for_update(group_id)

        if phase is None or group is None:
            raise TournamentErrors.GroupNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )
        group.name = Group.create(phase=phase, name=name).name

        self.group_repository.save(group)
