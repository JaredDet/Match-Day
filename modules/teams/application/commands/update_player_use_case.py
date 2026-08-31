from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.domain.player import PlayerPosition
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository

_UNSET = object()


class UpdatePlayerUseCase:
    @inject
    def __init__(self, player_repository: PlayerRepository):
        self.player_repository = player_repository

    @transaction.atomic
    def execute(
        self,
        *,
        team_id: UUID,
        player_id: UUID,
        name: str | object = _UNSET,
        preferred_position: PlayerPosition | None | object = _UNSET,
        preferred_shirt_number: int | None | object = _UNSET,
    ) -> None:
        player = self.player_repository.get_for_update(player_id)
        if player is None or player.team_id != team_id:
            raise TeamErrors.PlayerNotFound

        if name is not _UNSET:
            player.rename(name)
            if self.player_repository.exists_other_by_name(
                team_id=team_id,
                name=player.name,
                player_id=player.id,
            ):
                raise TeamErrors.PlayerAlreadyExists
        if preferred_position is not _UNSET or preferred_shirt_number is not _UNSET:
            player.update_profile(
                preferred_position=(
                    player.preferred_position
                    if preferred_position is _UNSET
                    else preferred_position
                ),
                preferred_shirt_number=(
                    player.preferred_shirt_number
                    if preferred_shirt_number is _UNSET
                    else preferred_shirt_number
                ),
            )
            if player.preferred_shirt_number is not None and (
                self.player_repository.exists_by_preferred_shirt_number(
                    team_id=team_id,
                    preferred_shirt_number=player.preferred_shirt_number,
                    excluding_player_id=player.id,
                )
            ):
                raise TeamErrors.PlayerShirtNumberAlreadyExists
        self.player_repository.save(player)
