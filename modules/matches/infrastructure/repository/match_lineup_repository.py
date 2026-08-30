from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_lineup_player import MatchLineupPlayer


class MatchLineupRepository:
    def replace(
        self,
        *,
        match_id,
        team_side: TeamSide,
        players: list[MatchLineupPlayer],
    ) -> None:
        MatchLineupPlayer.objects.filter(
            match_id=match_id,
            team_side=team_side,
        ).delete()
        MatchLineupPlayer.objects.bulk_create(players)
