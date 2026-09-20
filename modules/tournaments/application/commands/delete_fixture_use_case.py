from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.fixture_repository import FixtureRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class DeleteFixtureUseCase:
    @inject
    def __init__(
        self, fixture_repository: FixtureRepository, structure_repository: StructureRepository
    ):
        self.fixture_repository = fixture_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(self, *, fixture_id: UUID) -> None:
        entity = self.fixture_repository.get(fixture_id)

        if entity is None:
            raise TournamentErrors.FixtureNotFound

        phase = self.structure_repository.lock_phase(entity.phase_id)
        entity = self.fixture_repository.get_for_update(fixture_id)

        if phase is None or entity is None:
            raise TournamentErrors.FixtureNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        self.structure_repository.delete(entity)
