from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.domain.player import Player, PlayerPosition
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
    def execute(
        self,
        *,
        team_id: UUID,
        name: str,
        preferred_position: PlayerPosition | None = None,
        preferred_shirt_number: int | None = None,
    ) -> UUID:
        team = self.team_repository.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound
        player = Player.create(
            team_id=team.id,
            name=name,
            preferred_position=preferred_position,
            preferred_shirt_number=preferred_shirt_number,
        )
        if self.player_repository.exists_by_name(team.id, player.name):
            raise TeamErrors.PlayerAlreadyExists
        if preferred_shirt_number is not None and (
            self.player_repository.exists_by_preferred_shirt_number(
                team_id=team.id,
                preferred_shirt_number=preferred_shirt_number,
            )
        ):
            raise TeamErrors.PlayerShirtNumberAlreadyExists
        self.player_repository.save(player)
        return player.id
