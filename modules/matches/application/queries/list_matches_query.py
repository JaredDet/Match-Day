from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from injector import inject

from modules.matches.application.queries.team_detail import TeamDetail
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)


@dataclass(frozen=True, slots=True)
class MatchSummary:
    id: UUID
    status: MatchStatus
    current_period: MatchPeriod | None
    current_minute: int | None
    current_added_minute: int
    scheduled_at: datetime
    home_team: TeamDetail
    away_team: TeamDetail


class ListMatchesQuery:
    @inject
    def __init__(self, match_query_repository: MatchQueryRepository):
        self.match_query_repository = match_query_repository

    def execute(
        self,
        *,
        status: MatchStatus | None = None,
        date: date | None = None,
    ) -> tuple[MatchSummary, ...]:
        return self.match_query_repository.list(status=status, date=date)
