from modules.matches.domain.match_event import TeamSide
from tests.mothers.matches.match_mother import MatchMother


class GoalMother:
    @staticmethod
    def create(
        *,
        match=None,
        team_side: str = TeamSide.HOME,
        player_name: str = "Jugador Local",
        minute: int = 10,
    ):
        match = match or MatchMother.create(status="live")
        return match.register_goal(
            team_side=team_side,
            player_name=player_name,
            minute=minute,
        )
