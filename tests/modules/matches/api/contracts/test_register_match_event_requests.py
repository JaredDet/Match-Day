from uuid import uuid4

from modules.matches.api.contracts.requests.register_injury_request import (
    RegisterInjuryRequest,
)
from modules.matches.api.contracts.requests.register_penalty_attempt_request import (
    RegisterPenaltyAttemptRequest,
)
from modules.matches.api.contracts.requests.register_var_review_request import (
    RegisterVarReviewRequest,
)
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.penalty_attempt import PenaltyAttemptOutcome
from modules.matches.domain.var_review import VarReviewDecision, VarReviewReason


def test_parses_penalty_attempt():
    request = RegisterPenaltyAttemptRequest(
        data={
            "player_id": str(uuid4()),
            "outcome": "hit_post",
            "minute": 45,
            "added_minute": 2,
        }
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["outcome"] == PenaltyAttemptOutcome.HIT_POST


def test_parses_injury():
    player_id = uuid4()
    request = RegisterInjuryRequest(data={"player_id": str(player_id), "minute": 30})

    assert request.is_valid(), request.errors
    assert request.validated_data == {
        "player_id": player_id,
        "minute": 30,
        "added_minute": 0,
    }


def test_parses_var_review():
    reviewed_event_id = uuid4()
    request = RegisterVarReviewRequest(
        data={
            "team_side": "away",
            "reason": "direct_red_card",
            "decision": "changed",
            "reviewed_event_id": str(reviewed_event_id),
            "minute": 70,
        }
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["team_side"] == TeamSide.AWAY
    assert request.validated_data["reason"] == VarReviewReason.DIRECT_RED_CARD
    assert request.validated_data["decision"] == VarReviewDecision.CHANGED
    assert request.validated_data["reviewed_event_id"] == reviewed_event_id


def test_rejects_invalid_event_enums():
    penalty_request = RegisterPenaltyAttemptRequest(
        data={"player_id": str(uuid4()), "outcome": "scored", "minute": 10}
    )
    var_request = RegisterVarReviewRequest(
        data={
            "team_side": "neutral",
            "reason": "offside",
            "decision": "unknown",
            "minute": 10,
        }
    )

    assert not penalty_request.is_valid()
    assert not var_request.is_valid()
