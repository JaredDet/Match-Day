from modules.matches.domain.card import CardType
from modules.matches.domain.match_event import TeamSide
from tests.mothers.matches.match_mother import MatchMother


class CardMother:
    @staticmethod
    def create(
        *,
        match=None,
        team_side: str = TeamSide.AWAY,
        player_name: str = "Jugador Visitante",
        card_type: str = CardType.YELLOW,
        minute: int = 20,
    ):
        match = match or MatchMother.create(status="live")
        return match.register_card(
            team_side=team_side,
            player_name=player_name,
            card_type=card_type,
            minute=minute,
        )
