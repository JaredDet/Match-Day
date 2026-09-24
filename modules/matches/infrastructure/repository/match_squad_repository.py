from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import (
    MatchSquadPlayer,
)


class MatchSquadRepository:
    def list_eligible_player_ids(self, *, match_id, team_side: TeamSide) -> set:
        return set(
            MatchSquadPlayer.objects.filter(
                match_id=match_id,
                team_side=team_side,
                is_on_field=True,
                is_sent_off=False,
            ).values_list("player_id", flat=True)
        )

    def list_for_update(self, *, match_id) -> list[MatchSquadPlayer]:
        return list(MatchSquadPlayer.objects.select_for_update().filter(match_id=match_id))

    def list_on_field_for_update(self, *, match_id, team_side: TeamSide) -> list[MatchSquadPlayer]:
        return list(
            MatchSquadPlayer.objects.select_for_update().filter(
                match_id=match_id, team_side=team_side, is_on_field=True, is_sent_off=False
            )
        )

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
        MatchSquadPlayer.objects.bulk_update(
            players,
            ["is_on_field", "is_sent_off", "sent_off_reason", "position_x", "position_y"],
        )

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
