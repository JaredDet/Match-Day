from modules.matches.domain.card import Card
from modules.matches.domain.corner_kick import CornerKick
from modules.matches.domain.foul import Foul
from modules.matches.domain.goal import Goal, GoalType
from modules.matches.domain.injury import Injury
from modules.matches.domain.match import Match
from modules.matches.domain.match_squad_player import MatchSquadPlayer, MatchSquadRole
from modules.matches.domain.match_substitution import MatchSubstitution, SubstitutionReason
from modules.matches.domain.offside import Offside
from modules.matches.domain.penalty_attempt import PenaltyAttempt, PenaltyAttemptOutcome
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootout,
    PenaltyShootoutDepartureReason,
    PenaltyShootoutIneligibilityReason,
    PenaltyShootoutKick,
    PenaltyShootoutParticipant,
    PenaltyShootoutStatus,
)
from modules.matches.domain.shot import Shot, ShotOutcome
from modules.matches.domain.var_review import VarReview, VarReviewDecision, VarReviewReason

__all__ = [
    "Card",
    "CornerKick",
    "Foul",
    "Goal",
    "GoalType",
    "Injury",
    "Match",
    "MatchSquadPlayer",
    "MatchSquadRole",
    "MatchSubstitution",
    "Offside",
    "SubstitutionReason",
    "Shot",
    "ShotOutcome",
    "PenaltyAttempt",
    "PenaltyAttemptOutcome",
    "PenaltyKickOutcome",
    "PenaltyShootoutDepartureReason",
    "PenaltyShootoutIneligibilityReason",
    "PenaltyShootout",
    "PenaltyShootoutKick",
    "PenaltyShootoutParticipant",
    "PenaltyShootoutStatus",
    "VarReview",
    "VarReviewDecision",
    "VarReviewReason",
]
