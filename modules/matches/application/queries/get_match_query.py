from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from injector import inject

from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole, SentOffReason
from modules.matches.domain.match_substitution import SubstitutionReason
from modules.matches.domain.penalty_attempt import PenaltyAttemptOutcome
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootoutIneligibilityReason,
    PenaltyShootoutStatus,
)
from modules.matches.domain.var_review import VarReviewDecision, VarReviewReason
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)


class MatchEventType(StrEnum):
    GOAL = "goal"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    PENALTY_ATTEMPT = "penalty_attempt"
    INJURY = "injury"
    VAR_REVIEW = "var_review"
    PENALTY_SHOOTOUT_KICK = "penalty_shootout_kick"


@dataclass(frozen=True, slots=True)
class MatchEventDetail:
    id: UUID
    type: MatchEventType
    team_side: TeamSide
    minute: int | None = None
    period: MatchPeriod | None = None
    added_minute: int | None = None
    player_id: UUID | None = None
    player_name: str | None = None
    assist_player_id: UUID | None = None
    assist_player_name: str | None = None
    player_out_id: UUID | None = None
    player_out_name: str | None = None
    player_in_id: UUID | None = None
    player_in_name: str | None = None
    substitution_reason: SubstitutionReason | None = None
    goal_type: str | None = None
    penalty_outcome: PenaltyAttemptOutcome | None = None
    var_reason: VarReviewReason | None = None
    var_decision: VarReviewDecision | None = None
    reviewed_event_id: UUID | None = None
    sequence_number: int | None = None
    outcome: PenaltyKickOutcome | None = None


@dataclass(frozen=True, slots=True)
class PenaltyShootoutParticipantDetail:
    player_id: UUID
    player_name: str
    team_side: TeamSide
    is_eligible: bool
    ineligibility_reason: PenaltyShootoutIneligibilityReason | None
    became_ineligible_at: datetime | None


@dataclass(frozen=True, slots=True)
class PenaltyShootoutDetail:
    status: PenaltyShootoutStatus
    starting_team_side: TeamSide
    next_team_side: TeamSide | None
    home_participant_ids: tuple[UUID, ...]
    away_participant_ids: tuple[UUID, ...]
    home_score: int
    away_score: int
    winner_team_side: TeamSide | None
    participants: tuple[PenaltyShootoutParticipantDetail, ...]


@dataclass(frozen=True, slots=True)
class MatchSquadPlayerDetail:
    player_id: UUID
    player_name: str
    team_side: TeamSide
    shirt_number: int
    role: MatchSquadRole
    is_on_field: bool
    is_sent_off: bool
    sent_off_reason: SentOffReason | None
    is_captain: bool


@dataclass(frozen=True, slots=True)
class MatchTeamDetail:
    id: UUID
    name: str
    head_coach_name: str | None
    team_side: TeamSide
    goals: int
    penalty_score: int | None
    formation: MatchFormation | None
    lineup: tuple[MatchSquadPlayerDetail, ...]


@dataclass(frozen=True, slots=True)
class MatchDetail:
    id: UUID
    status: MatchStatus
    current_period: MatchPeriod | None
    current_minute: int | None
    current_added_minute: int
    scheduled_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    stadium_name: str | None
    referee_name: str | None
    home_team: MatchTeamDetail
    away_team: MatchTeamDetail
    events: tuple[MatchEventDetail, ...]
    penalty_shootout: PenaltyShootoutDetail | None


class GetMatchQuery:
    @inject
    def __init__(self, match_query_repository: MatchQueryRepository):
        self.match_query_repository = match_query_repository

    def execute(self, match_id: UUID) -> MatchDetail:
        match = self.match_query_repository.get(match_id)

        if match is None:
            raise MatchErrors.NotFound

        return match
