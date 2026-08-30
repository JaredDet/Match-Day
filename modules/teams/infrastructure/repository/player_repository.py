from uuid import UUID

from modules.teams.domain.player import Player


class PlayerRepository:
    def get(self, player_id: UUID) -> Player | None:
        return Player.objects.select_related("team").filter(id=player_id).first()

    def save(self, player: Player) -> None:
        player.save()
