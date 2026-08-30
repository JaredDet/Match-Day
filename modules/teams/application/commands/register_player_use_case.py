from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.domain.player import Player
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class RegisterPlayerUseCase:
    @inject
    def __init__(
        self,
        player_repository: PlayerRepository,
        team_repository: TeamRepository,
    ):
        self.player_repository = player_repository
        self.team_repository = team_repository

    @transaction.atomic
    def execute(self, *, team_id: UUID, name: str) -> UUID:
        team = self.team_repository.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound
        player = Player.create(team=team, name=name)
        if self.player_repository.exists_by_name(team.id, player.name):
            raise TeamErrors.PlayerAlreadyExists
        self.player_repository.save(player)
        return player.id
