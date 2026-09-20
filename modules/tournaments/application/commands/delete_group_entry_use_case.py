from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.group_entry_repository import (
    GroupEntryRepository,
)
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class DeleteGroupEntryUseCase:
    @inject
    def __init__(
        self,
        group_entry_repository: GroupEntryRepository,
        structure_repository: StructureRepository,
    ):
        self.group_entry_repository = group_entry_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, group_entry_id: UUID) -> None:
        entity = self.group_entry_repository.get(group_entry_id)

        if entity is None:
            raise TournamentErrors.GroupEntryNotFound

        phase = self.structure_repository.lock_phase(entity.phase_id)
        entity = self.group_entry_repository.get_for_update(group_entry_id)

        if phase is None or entity is None:
            raise TournamentErrors.GroupEntryNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        if self.structure_repository.entry_has_fixtures(entity):
            raise TournamentErrors.HasDependencies

        self.structure_repository.clear_tie_break(entity.group_id)

        self.structure_repository.delete(entity)
