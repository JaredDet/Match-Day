import pytest
from injector import UnsatisfiedRequirement

from core.dependency_injector import injector_instance
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.application.commands.set_match_lineup_use_case import SetMatchLineupUseCase
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.list_matches_query import ListMatchesQuery
from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
from modules.teams.application.commands.register_team_squad_use_case import (
    RegisterTeamSquadUseCase,
)
from modules.teams.application.commands.update_team_use_case import UpdateTeamUseCase
from modules.teams.application.queries.get_team_query import GetTeamQuery
from modules.teams.application.queries.list_teams_query import ListTeamsQuery


def test_rejects_unregistered_dependencies():
    class ExampleService:
        pass

    with pytest.raises(UnsatisfiedRequirement):
        injector_instance.get(ExampleService)


@pytest.mark.parametrize(
    "dependency",
    [
        CreateTeamUseCase,
        RegisterTeamSquadUseCase,
        UpdateTeamUseCase,
        CreateMatchUseCase,
        SetMatchLineupUseCase,
        StartMatchUseCase,
        RegisterGoalUseCase,
        RegisterCardUseCase,
        DisallowGoalUseCase,
        RescindCardUseCase,
        FinishMatchUseCase,
        ListMatchesQuery,
        GetMatchQuery,
        ListTeamsQuery,
        GetTeamQuery,
    ],
)
def test_resolves_demo_dependencies(dependency):
    assert isinstance(injector_instance.get(dependency), dependency)
