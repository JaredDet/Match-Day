from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.group_entry_repository import (
    GroupEntryRepository,
)
from modules.tournaments.infrastructure.repository.group_repository import GroupRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class SetGroupTieBreakUseCase:
    @inject
    def __init__(
        self,
        group_repository: GroupRepository,
        group_entry_repository: GroupEntryRepository,
        structure_repository: StructureRepository,
    ):
        self.group_repository = group_repository
        self.group_entry_repository = group_entry_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, group_id: UUID, team_ids: list[UUID]) -> None:
        group = self.group_repository.get(group_id)

        if group is None:
            raise TournamentErrors.GroupNotFound

        phase = self.structure_repository.lock_phase(group.phase_id)
        group = self.group_repository.get_for_update(group_id)

        if phase is None or group is None:
            raise TournamentErrors.GroupNotFound

        if self.structure_repository.has_successors(phase.id):
            raise TournamentErrors.StructureLocked

        if len(set(team_ids)) != len(team_ids) or set(
            team_ids
        ) != self.group_entry_repository.team_ids(group.id):
            raise TournamentErrors.InvalidTieBreak

        group.tie_break_order = [str(team_id) for team_id in team_ids]

        self.group_repository.save(group)
