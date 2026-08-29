from modules.matches.api.contracts.requests.register_card_request import RegisterCardRequest
from modules.matches.domain.card import CardType
from modules.matches.domain.match_event import TeamSide


def test_parses_card_request_strings_as_enums():
    request = RegisterCardRequest(
        data={
            "team_side": "away",
            "player_name": "Defensor",
            "card_type": "yellow",
            "minute": 51,
        }
    )

    assert request.is_valid(), request.errors
    assert request.validated_data["team_side"] is TeamSide.AWAY
    assert request.validated_data["card_type"] is CardType.YELLOW


def test_rejects_unknown_card_type():
    request = RegisterCardRequest(
        data={
            "team_side": "home",
            "player_name": "Jugador",
            "card_type": "blue",
            "minute": 10,
        }
    )

    assert not request.is_valid()
    assert "card_type" in request.errors
