from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.phase import PhaseStatus
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.phase_repository import PhaseRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class SetPhaseStatusUseCase:
    @inject
    def __init__(
        self, phase_repository: PhaseRepository, structure_repository: StructureRepository
    ):
        self.phase_repository = phase_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, phase_id: UUID, status: PhaseStatus) -> None:
        phase = self.structure_repository.lock_phase(phase_id)

        if phase is None:
            raise TournamentErrors.PhaseNotFound

        if phase.generated or self.structure_repository.has_successors(phase.id):
            raise TournamentErrors.StructureLocked

        phase.set_status(status)
        self.phase_repository.save(phase)
