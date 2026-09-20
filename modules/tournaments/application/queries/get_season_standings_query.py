from dataclasses import dataclass
from uuid import UUID

from injector import inject

from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.competition_query_repository import (
    CompetitionQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.season_query_repository import (
    SeasonQueryRepository,
)


@dataclass(frozen=True, slots=True)
class StandingRow:
    id: UUID
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    played: int
    goal_difference: int
    points: int
    qualified: bool
    tie_break_required: bool = False


@dataclass(frozen=True, slots=True)
class StandingGroup:
    id: UUID
    name: str
    phase_id: UUID
    status: str
    matchdays: int
    rows: tuple[StandingRow, ...]


class GetSeasonStandingsQuery:
    @inject
    def __init__(
        self,
        season_query_repository: SeasonQueryRepository,
        competition_query_repository: CompetitionQueryRepository,
    ):
        self.season_query_repository = season_query_repository
        self.competition_query_repository = competition_query_repository

    def execute(self, season_id: UUID) -> tuple[StandingGroup, ...]:
        if self.season_query_repository.get(season_id) is None:
            raise TournamentErrors.SeasonNotFound

        return self.competition_query_repository.standings(season_id)
