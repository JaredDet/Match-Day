from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.domain.player import Player
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class RegisterTeamSquadUseCase:
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
        players_data: list[dict] | None = None,
        player_names: list[str] | None = None,
    ) -> tuple[UUID, ...]:
        team = self.team_repository.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound

        resolved_players_data = players_data or [
            {"name": name} for name in (player_names or [])
        ]
        players = [
            Player.create(team_id=team.id, **data) for data in resolved_players_data
        ]
        normalized_names = [player.name.casefold() for player in players]
        if len(normalized_names) != len(set(normalized_names)):
            raise TeamErrors.PlayerAlreadyExists
        if any(self.player_repository.exists_by_name(team.id, player.name) for player in players):
            raise TeamErrors.PlayerAlreadyExists

        shirt_numbers = [
            player.preferred_shirt_number
            for player in players
            if player.preferred_shirt_number is not None
        ]
        if len(shirt_numbers) != len(set(shirt_numbers)):
            raise TeamErrors.PlayerShirtNumberAlreadyExists
        if any(
            self.player_repository.exists_by_preferred_shirt_number(
                team_id=team.id,
                preferred_shirt_number=shirt_number,
            )
            for shirt_number in shirt_numbers
        ):
            raise TeamErrors.PlayerShirtNumberAlreadyExists

        self.player_repository.save_all(players)
        return tuple(player.id for player in players)
