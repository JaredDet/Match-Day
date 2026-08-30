from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository


class UpdatePlayerUseCase:
    @inject
    def __init__(self, player_repository: PlayerRepository):
        self.player_repository = player_repository

    @transaction.atomic
    def execute(self, *, team_id: UUID, player_id: UUID, name: str) -> None:
        player = self.player_repository.get_for_update(player_id)
        if player is None or player.team_id != team_id:
            raise TeamErrors.PlayerNotFound

        player.rename(name)
        if self.player_repository.exists_other_by_name(
            team_id=team_id,
            name=player.name,
            player_id=player.id,
        ):
            raise TeamErrors.PlayerAlreadyExists
        self.player_repository.save(player)
