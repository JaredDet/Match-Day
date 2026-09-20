from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.phase import Phase, PhaseKind, PhaseStatus
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.phase_repository import PhaseRepository
from modules.tournaments.infrastructure.repository.season_repository import SeasonRepository


class CreatePhaseUseCase:
    @inject
    def __init__(self, phase_repository: PhaseRepository, season_repository: SeasonRepository):
        self.phase_repository = phase_repository
        self.season_repository = season_repository

    @transaction.atomic
    def execute(
        self,
        *,
        season_id: UUID,
        name: str,
        kind: PhaseKind,
        order: int,
        status: PhaseStatus = PhaseStatus.SCHEDULED,
        qualifying_teams: int = 2,
        matchdays: int = 1,
    ) -> UUID:
        if self.season_repository.get_for_update(season_id) is None:
            raise TournamentErrors.SeasonNotFound

        phase = Phase.create(
            season_id=season_id,
            name=name,
            kind=kind,
            order=order,
            status=status,
            qualifying_teams=qualifying_teams,
            matchdays=matchdays,
        )

        self.phase_repository.save(phase)

        return phase.id
