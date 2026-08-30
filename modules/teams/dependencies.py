import injector

from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
from modules.teams.application.commands.register_player_use_case import RegisterPlayerUseCase
from modules.teams.application.commands.register_team_squad_use_case import (
    RegisterTeamSquadUseCase,
)
from modules.teams.application.commands.set_team_captain_use_case import SetTeamCaptainUseCase
from modules.teams.application.commands.update_player_use_case import UpdatePlayerUseCase
from modules.teams.application.commands.update_team_use_case import UpdateTeamUseCase
from modules.teams.application.queries.get_player_query import GetPlayerQuery
from modules.teams.application.queries.get_team_query import GetTeamQuery
from modules.teams.application.queries.list_players_query import ListPlayersQuery
from modules.teams.application.queries.list_teams_query import ListTeamsQuery
from modules.teams.infrastructure.query_repository.player_query_repository import (
    PlayerQueryRepository,
)
from modules.teams.infrastructure.query_repository.team_query_repository import (
    TeamQueryRepository,
)
from modules.teams.infrastructure.repository.player_repository import PlayerRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository


class TeamsModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(PlayerRepository, to=PlayerRepository, scope=injector.singleton)
        binder.bind(TeamRepository, to=TeamRepository, scope=injector.singleton)
        binder.bind(TeamQueryRepository, to=TeamQueryRepository, scope=injector.singleton)
        binder.bind(PlayerQueryRepository, to=PlayerQueryRepository, scope=injector.singleton)
        binder.bind(CreateTeamUseCase, to=CreateTeamUseCase, scope=injector.singleton)
        binder.bind(UpdateTeamUseCase, to=UpdateTeamUseCase, scope=injector.singleton)
        binder.bind(UpdatePlayerUseCase, to=UpdatePlayerUseCase, scope=injector.singleton)
        binder.bind(SetTeamCaptainUseCase, to=SetTeamCaptainUseCase, scope=injector.singleton)
        binder.bind(RegisterPlayerUseCase, to=RegisterPlayerUseCase, scope=injector.singleton)
        binder.bind(
            RegisterTeamSquadUseCase,
            to=RegisterTeamSquadUseCase,
            scope=injector.singleton,
        )
        binder.bind(ListTeamsQuery, to=ListTeamsQuery, scope=injector.singleton)
        binder.bind(GetTeamQuery, to=GetTeamQuery, scope=injector.singleton)
        binder.bind(ListPlayersQuery, to=ListPlayersQuery, scope=injector.singleton)
        binder.bind(GetPlayerQuery, to=GetPlayerQuery, scope=injector.singleton)
