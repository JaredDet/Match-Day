import injector

from modules.teams.infrastructure.repository.player_repository import PlayerRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class TeamsModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(PlayerRepository, to=PlayerRepository, scope=injector.singleton)
        binder.bind(TeamRepository, to=TeamRepository, scope=injector.singleton)
