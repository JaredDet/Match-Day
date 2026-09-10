from uuid import uuid4

from modules.matches.api.contracts.requests.reduce_penalty_shootout_participants_request import (
    ReducePenaltyShootoutParticipantsRequest,
)
from modules.matches.domain.penalty_shootout import PenaltyShootoutDepartureReason


def test_parses_penalty_shootout_participant_reduction():
    unavailable_player_id = uuid4()
    opponent_player_id = uuid4()
    request = ReducePenaltyShootoutParticipantsRequest(
        data={
            "unavailable_player_id": str(unavailable_player_id),
            "departure_reason": "injury",
            "opponent_excluded_player_id": str(opponent_player_id),
        },
    )

    assert request.is_valid(), request.errors
    assert request.validated_data == {
        "unavailable_player_id": unavailable_player_id,
        "departure_reason": PenaltyShootoutDepartureReason.INJURY,
        "opponent_excluded_player_id": opponent_player_id,
    }
