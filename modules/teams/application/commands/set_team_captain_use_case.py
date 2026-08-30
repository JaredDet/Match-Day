from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class SetTeamCaptainUseCase:
    @inject
    def __init__(
        self,
        team_repository: TeamRepository,
        player_repository: PlayerRepository,
    ):
        self.team_repository = team_repository
        self.player_repository = player_repository

    @transaction.atomic
    def execute(self, *, team_id: UUID, player_id: UUID) -> None:
        team = self.team_repository.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound
        player = self.player_repository.get(player_id)
        if player is None:
            raise TeamErrors.PlayerNotFound

        team.assign_captain(player)
        self.team_repository.save(team)
