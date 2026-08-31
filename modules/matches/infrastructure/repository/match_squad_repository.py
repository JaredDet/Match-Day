from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import (
    MatchSquadPlayer,
    MatchSquadRole,
)


class MatchSquadRepository:
    def is_starter(self, *, match_id, player_id) -> bool:
        return MatchSquadPlayer.objects.filter(
            match_id=match_id,
            player_id=player_id,
            role=MatchSquadRole.STARTER,
        ).exists()

    def replace(
        self,
        *,
        match_id,
        team_side: TeamSide,
        players: list[MatchSquadPlayer],
    ) -> None:
        MatchSquadPlayer.objects.filter(
            match_id=match_id,
            team_side=team_side,
        ).delete()
        MatchSquadPlayer.objects.bulk_create(players)
