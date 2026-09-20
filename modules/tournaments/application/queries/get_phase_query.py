from uuid import UUID

from injector import inject

from modules.tournaments.application.queries.list_phases_query import PhaseSummary
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.phase_query_repository import (
    PhaseQueryRepository,
)


class GetPhaseQuery:
    @inject
    def __init__(self, phase_query_repository: PhaseQueryRepository):
        self.phase_query_repository = phase_query_repository

    def execute(self, phase_id: UUID) -> PhaseSummary:
        result = self.phase_query_repository.get(phase_id)

        if result is None:
            raise TournamentErrors.PhaseNotFound

        return result
