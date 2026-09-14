import pytest
from injector import UnsatisfiedRequirement

from core.dependency_injector import injector_instance
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.application.commands.end_match_period_use_case import EndMatchPeriodUseCase
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.application.commands.finish_penalty_shootout_use_case import (
    FinishPenaltyShootoutUseCase,
)
from modules.matches.application.commands.reduce_penalty_shootout_participants_use_case import (
    ReducePenaltyShootoutParticipantsUseCase,
)
from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.application.commands.register_corner_kick_use_case import (
    RegisterCornerKickUseCase,
)
from modules.matches.application.commands.register_foul_use_case import RegisterFoulUseCase
from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.application.commands.register_injury_use_case import RegisterInjuryUseCase
from modules.matches.application.commands.register_offside_use_case import RegisterOffsideUseCase
from modules.matches.application.commands.register_penalty_attempt_use_case import (
    RegisterPenaltyAttemptUseCase,
)
from modules.matches.application.commands.register_penalty_shootout_kick_use_case import (
    RegisterPenaltyShootoutKickUseCase,
)
from modules.matches.application.commands.register_shot_use_case import RegisterShotUseCase
from modules.matches.application.commands.register_substitution_use_case import (
    RegisterSubstitutionUseCase,
)
from modules.matches.application.commands.register_var_review_use_case import (
    RegisterVarReviewUseCase,
)
from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.application.commands.set_match_lineup_use_case import SetMatchLineupUseCase
from modules.matches.application.commands.set_match_period_added_time_use_case import (
    SetMatchPeriodAddedTimeUseCase,
)
from modules.matches.application.commands.start_match_period_use_case import StartMatchPeriodUseCase
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.application.commands.start_penalty_shootout_use_case import (
    StartPenaltyShootoutUseCase,
)
from modules.matches.application.commands.synchronize_match_clocks_use_case import (
    SynchronizeMatchClocksUseCase,
)
from modules.matches.application.commands.update_match_possession_use_case import (
    UpdateMatchPossessionUseCase,
)
from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.list_matches_query import ListMatchesQuery
from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
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
        UpdatePlayerUseCase,
        SetTeamCaptainUseCase,
        CreateMatchUseCase,
        SetMatchLineupUseCase,
        StartMatchUseCase,
        StartMatchPeriodUseCase,
        EndMatchPeriodUseCase,
        SetMatchPeriodAddedTimeUseCase,
        SynchronizeMatchClocksUseCase,
        UpdateMatchPossessionUseCase,
        RegisterGoalUseCase,
        RegisterFoulUseCase,
        RegisterCornerKickUseCase,
        RegisterOffsideUseCase,
        RegisterShotUseCase,
        RegisterPenaltyAttemptUseCase,
        RegisterInjuryUseCase,
        RegisterVarReviewUseCase,
        RegisterCardUseCase,
        RegisterSubstitutionUseCase,
        DisallowGoalUseCase,
        RescindCardUseCase,
        FinishMatchUseCase,
        StartPenaltyShootoutUseCase,
        RegisterPenaltyShootoutKickUseCase,
        ReducePenaltyShootoutParticipantsUseCase,
        FinishPenaltyShootoutUseCase,
        ListMatchesQuery,
        GetMatchQuery,
        ListTeamsQuery,
        GetTeamQuery,
        ListPlayersQuery,
        GetPlayerQuery,
    ],
)
def test_resolves_demo_dependencies(dependency):
    assert isinstance(injector_instance.get(dependency), dependency)
