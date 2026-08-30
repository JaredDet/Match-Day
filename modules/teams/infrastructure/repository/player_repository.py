from uuid import UUID

from django.db import IntegrityError

from modules.teams.domain.player import Player
from modules.teams.errors import TeamErrors


class PlayerRepository:
    def exists_by_name(self, team_id: UUID, name: str) -> bool:
        return Player.objects.filter(team_id=team_id, name__iexact=name).exists()

    def get(self, player_id: UUID) -> Player | None:
        return Player.objects.select_related("team").filter(id=player_id).first()

    def save(self, player: Player) -> None:
        try:
            player.save()
        except IntegrityError as error:
            if "unique_player_name_per_team" in str(error):
                raise TeamErrors.PlayerAlreadyExists from error
            raise

    def save_all(self, players: list[Player]) -> None:
        try:
            Player.objects.bulk_create(players)
        except IntegrityError as error:
            if "unique_player_name_per_team" in str(error):
                raise TeamErrors.PlayerAlreadyExists from error
            raise
