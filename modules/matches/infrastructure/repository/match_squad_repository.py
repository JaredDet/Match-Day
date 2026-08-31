from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import (
    MatchSquadPlayer,
)


class MatchSquadRepository:
    def is_on_field(self, *, match_id, player_id) -> bool:
        return MatchSquadPlayer.objects.filter(
            match_id=match_id,
            player_id=player_id,
            is_on_field=True,
        ).exists()

    def get_for_update(self, *, match_id, player_id) -> MatchSquadPlayer | None:
        return (
            MatchSquadPlayer.objects.select_for_update()
            .filter(match_id=match_id, player_id=player_id)
            .first()
        )

    def save_all(self, players: list[MatchSquadPlayer]) -> None:
        MatchSquadPlayer.objects.bulk_update(players, ["is_on_field"])

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
