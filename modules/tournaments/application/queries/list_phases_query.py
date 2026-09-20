from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from modules.tournaments.infrastructure.query_repository.phase_query_repository import (
    PhaseQueryRepository,
)


@dataclass(frozen=True, slots=True)
class PhaseSummary:
    id: UUID
    season_id: UUID
    name: str
    kind: str
    order: int
    status: str
    qualifying_teams: int
    matchdays: int
    generated: bool
    source_phase_id: UUID | None
    scheduled_at: datetime | None
    expected_matches: int | None


class ListPhasesQuery:
    @inject
    def __init__(self, phase_query_repository: PhaseQueryRepository):
        self.phase_query_repository = phase_query_repository

    def execute(self, *, season_id: UUID | None = None) -> tuple[PhaseSummary, ...]:
        return self.phase_query_repository.list(season_id=season_id)
