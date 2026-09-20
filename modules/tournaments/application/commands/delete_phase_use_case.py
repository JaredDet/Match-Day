from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.phase_repository import PhaseRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class DeletePhaseUseCase:
    @inject
    def __init__(
        self, phase_repository: PhaseRepository, structure_repository: StructureRepository
    ):
        self.phase_repository = phase_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, phase_id: UUID) -> None:
        entity = self.phase_repository.get(phase_id)

        if entity is None:
            raise TournamentErrors.PhaseNotFound

        phase = self.structure_repository.lock_phase(entity.id)
        entity = self.phase_repository.get_for_update(phase_id)

        if phase is None or entity is None:
            raise TournamentErrors.PhaseNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        if self.structure_repository.phase_has_dependencies(entity.id):
            raise TournamentErrors.HasDependencies

        self.structure_repository.delete(entity)
