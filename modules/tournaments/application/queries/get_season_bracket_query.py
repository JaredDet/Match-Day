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
class CupTie:
    id: UUID
    home_id: UUID
    away_id: UUID
    home_score: int | None
    away_score: int | None
    penalties: tuple[int, int] | None


@dataclass(frozen=True, slots=True)
class BracketRound:
    id: UUID
    name: str
    ties: tuple[CupTie, ...]


@dataclass(frozen=True, slots=True)
class SeasonBracket:
    rounds: tuple[BracketRound, ...]
    third: CupTie | None


class GetSeasonBracketQuery:
    @inject
    def __init__(
        self,
        season_query_repository: SeasonQueryRepository,
        competition_query_repository: CompetitionQueryRepository,
    ):
        self.season_query_repository = season_query_repository
        self.competition_query_repository = competition_query_repository

    def execute(self, season_id: UUID) -> SeasonBracket:
        if self.season_query_repository.get(season_id) is None:
            raise TournamentErrors.SeasonNotFound

        return self.competition_query_repository.bracket(season_id)
