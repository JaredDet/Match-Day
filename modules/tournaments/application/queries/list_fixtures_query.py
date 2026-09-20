from dataclasses import dataclass
from uuid import UUID

from injector import inject

from modules.tournaments.infrastructure.query_repository.fixture_query_repository import (
    FixtureQueryRepository,
)


@dataclass(frozen=True, slots=True)
class FixtureSummary:
    id: UUID
    phase_id: UUID
    group_id: UUID | None
    match_id: UUID
    position: int
    matchday: int


class ListFixturesQuery:
    @inject
    def __init__(self, fixture_query_repository: FixtureQueryRepository):
        self.fixture_query_repository = fixture_query_repository

    def execute(self, *, phase_id: UUID | None = None) -> tuple[FixtureSummary, ...]:
        return self.fixture_query_repository.list(phase_id=phase_id)
