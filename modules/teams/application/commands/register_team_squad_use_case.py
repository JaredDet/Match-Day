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
    def execute(self, *, team_id: UUID, player_names: list[str]) -> tuple[UUID, ...]:
        team = self.team_repository.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound

        players = [Player.create(team=team, name=name) for name in player_names]
        normalized_names = [player.name.casefold() for player in players]
        if len(normalized_names) != len(set(normalized_names)):
            raise TeamErrors.PlayerAlreadyExists
        if any(self.player_repository.exists_by_name(team.id, player.name) for player in players):
            raise TeamErrors.PlayerAlreadyExists

        self.player_repository.save_all(players)
        return tuple(player.id for player in players)
