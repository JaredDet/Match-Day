from uuid import UUID

from django.db import IntegrityError

from modules.teams.domain.player import Player
from modules.teams.errors import TeamErrors


class PlayerRepository:
    def exists_by_name(self, team_id: UUID, name: str) -> bool:
        return Player.objects.filter(team_id=team_id, name__iexact=name).exists()

    def get(self, player_id: UUID) -> Player | None:
        return Player.objects.select_related("team").filter(id=player_id).first()

    def get_for_update(self, player_id: UUID) -> Player | None:
        return Player.objects.select_for_update().filter(id=player_id).first()

    def exists_other_by_name(self, *, team_id: UUID, name: str, player_id: UUID) -> bool:
        return (
            Player.objects.filter(team_id=team_id, name__iexact=name).exclude(id=player_id).exists()
        )

    def exists_by_preferred_shirt_number(
        self,
        *,
        team_id: UUID,
        preferred_shirt_number: int,
        excluding_player_id: UUID | None = None,
    ) -> bool:
        players = Player.objects.filter(
            team_id=team_id,
            preferred_shirt_number=preferred_shirt_number,
        )
        if excluding_player_id is not None:
            players = players.exclude(id=excluding_player_id)
        return players.exists()

    def get_many(self, player_ids: list[UUID]) -> dict[UUID, Player]:
        return Player.objects.in_bulk(player_ids)

    def save(self, player: Player) -> None:
        try:
            player.save()
        except IntegrityError as error:
            if "unique_player_name_per_team" in str(error):
                raise TeamErrors.PlayerAlreadyExists from error
            if "unique_player_preferred_shirt_per_team" in str(error):
                raise TeamErrors.PlayerShirtNumberAlreadyExists from error
            raise

    def save_all(self, players: list[Player]) -> None:
        try:
            Player.objects.bulk_create(players)
        except IntegrityError as error:
            if "unique_player_name_per_team" in str(error):
                raise TeamErrors.PlayerAlreadyExists from error
            if "unique_player_preferred_shirt_per_team" in str(error):
                raise TeamErrors.PlayerShirtNumberAlreadyExists from error
            raise
