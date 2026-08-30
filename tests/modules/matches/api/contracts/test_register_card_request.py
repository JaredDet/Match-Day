from uuid import uuid4

from modules.matches.api.contracts.requests.register_card_request import RegisterCardRequest
from modules.matches.domain.card import CardType


def test_parses_card_type_and_player_id():
    player_id = uuid4()
    request = RegisterCardRequest(
        data={"player_id": str(player_id), "card_type": "yellow", "minute": 51}
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["player_id"] == player_id
    assert request.validated_data["card_type"] is CardType.YELLOW


def test_rejects_unknown_card_type():
    request = RegisterCardRequest(
        data={"player_id": str(uuid4()), "card_type": "blue", "minute": 10}
    )

    assert not request.is_valid()
    assert "card_type" in request.errors
