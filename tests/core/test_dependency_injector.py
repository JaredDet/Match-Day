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
from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.application.commands.delete_news_use_case import DeleteNewsUseCase
from modules.news.application.commands.publish_news_use_case import PublishNewsUseCase
from modules.news.application.commands.publish_scheduled_news_use_case import (
    PublishScheduledNewsUseCase,
)
from modules.news.application.commands.schedule_news_use_case import ScheduleNewsUseCase
from modules.news.application.commands.unschedule_news_use_case import (
    UnscheduleNewsUseCase,
)
from modules.news.application.commands.update_news_use_case import UpdateNewsUseCase
from modules.news.application.news_content_parser import NewsContentParser
from modules.news.application.queries.get_news_query import GetNewsQuery
from modules.news.application.queries.list_news_query import ListNewsQuery
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
from modules.tournaments.application.commands.add_season_team_use_case import AddSeasonTeamUseCase
from modules.tournaments.application.commands.advance_bracket_use_case import AdvanceBracketUseCase
from modules.tournaments.application.commands.create_fixture_use_case import CreateFixtureUseCase
from modules.tournaments.application.commands.create_group_entry_use_case import (
    CreateGroupEntryUseCase,
)
from modules.tournaments.application.commands.create_group_use_case import CreateGroupUseCase
from modules.tournaments.application.commands.create_phase_use_case import CreatePhaseUseCase
from modules.tournaments.application.commands.create_season_use_case import CreateSeasonUseCase
from modules.tournaments.application.commands.create_tournament_use_case import (
    CreateTournamentUseCase,
)
from modules.tournaments.application.commands.delete_fixture_use_case import DeleteFixtureUseCase
from modules.tournaments.application.commands.delete_group_entry_use_case import (
    DeleteGroupEntryUseCase,
)
from modules.tournaments.application.commands.delete_group_use_case import DeleteGroupUseCase
from modules.tournaments.application.commands.delete_phase_use_case import DeletePhaseUseCase
from modules.tournaments.application.commands.generate_bracket_use_case import (
    GenerateBracketUseCase,
)
from modules.tournaments.application.commands.remove_season_team_use_case import (
    RemoveSeasonTeamUseCase,
)
from modules.tournaments.application.commands.set_group_tie_break_use_case import (
    SetGroupTieBreakUseCase,
)
from modules.tournaments.application.commands.set_phase_status_use_case import SetPhaseStatusUseCase
from modules.tournaments.application.commands.update_fixture_use_case import UpdateFixtureUseCase
from modules.tournaments.application.commands.update_group_use_case import UpdateGroupUseCase
from modules.tournaments.application.commands.update_phase_use_case import UpdatePhaseUseCase
from modules.tournaments.application.queries.get_fixture_query import GetFixtureQuery
from modules.tournaments.application.queries.get_group_entry_query import GetGroupEntryQuery
from modules.tournaments.application.queries.get_group_query import GetGroupQuery
from modules.tournaments.application.queries.get_phase_query import GetPhaseQuery
from modules.tournaments.application.queries.get_season_bracket_query import GetSeasonBracketQuery
from modules.tournaments.application.queries.get_season_query import GetSeasonQuery
from modules.tournaments.application.queries.get_season_standings_query import (
    GetSeasonStandingsQuery,
)
from modules.tournaments.application.queries.get_tournament_query import GetTournamentQuery
from modules.tournaments.application.queries.list_fixtures_query import ListFixturesQuery
from modules.tournaments.application.queries.list_group_entries_query import ListGroupEntriesQuery
from modules.tournaments.application.queries.list_groups_query import ListGroupsQuery
from modules.tournaments.application.queries.list_phases_query import ListPhasesQuery
from modules.tournaments.application.queries.list_season_fixtures_query import (
    ListSeasonFixturesQuery,
)
from modules.tournaments.application.queries.list_seasons_query import ListSeasonsQuery
from modules.tournaments.application.queries.list_tournaments_query import ListTournamentsQuery


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
        CreateNewsUseCase,
        UpdateNewsUseCase,
        NewsContentParser,
        ScheduleNewsUseCase,
        PublishNewsUseCase,
        PublishScheduledNewsUseCase,
        UnscheduleNewsUseCase,
        DeleteNewsUseCase,
        ListMatchesQuery,
        GetMatchQuery,
        ListTeamsQuery,
        GetTeamQuery,
        ListPlayersQuery,
        GetPlayerQuery,
        ListNewsQuery,
        GetNewsQuery,
        CreateTournamentUseCase,
        AddSeasonTeamUseCase,
        RemoveSeasonTeamUseCase,
        UpdatePhaseUseCase,
        UpdateGroupUseCase,
        UpdateFixtureUseCase,
        DeletePhaseUseCase,
        DeleteGroupUseCase,
        DeleteFixtureUseCase,
        DeleteGroupEntryUseCase,
        SetGroupTieBreakUseCase,
        GenerateBracketUseCase,
        AdvanceBracketUseCase,
        CreateSeasonUseCase,
        CreatePhaseUseCase,
        CreateGroupUseCase,
        CreateGroupEntryUseCase,
        CreateFixtureUseCase,
        SetPhaseStatusUseCase,
        ListTournamentsQuery,
        GetTournamentQuery,
        ListSeasonsQuery,
        GetSeasonQuery,
        ListPhasesQuery,
        GetPhaseQuery,
        ListGroupsQuery,
        GetGroupQuery,
        ListGroupEntriesQuery,
        GetGroupEntryQuery,
        ListFixturesQuery,
        GetFixtureQuery,
        GetSeasonStandingsQuery,
        GetSeasonBracketQuery,
        ListSeasonFixturesQuery,
    ],
)
def test_resolves_demo_dependencies(dependency):
    assert isinstance(injector_instance.get(dependency), dependency)
