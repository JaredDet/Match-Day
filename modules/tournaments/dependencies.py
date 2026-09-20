import injector

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
from modules.tournaments.infrastructure.query_repository.competition_query_repository import (
    CompetitionQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.fixture_query_repository import (
    FixtureQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.group_entry_query_repository import (
    GroupEntryQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.group_query_repository import (
    GroupQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.phase_query_repository import (
    PhaseQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.season_query_repository import (
    SeasonQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.tournament_query_repository import (
    TournamentQueryRepository,
)
from modules.tournaments.infrastructure.repository.bracket_repository import BracketRepository
from modules.tournaments.infrastructure.repository.fixture_repository import FixtureRepository
from modules.tournaments.infrastructure.repository.group_entry_repository import (
    GroupEntryRepository,
)
from modules.tournaments.infrastructure.repository.group_repository import GroupRepository
from modules.tournaments.infrastructure.repository.phase_repository import PhaseRepository
from modules.tournaments.infrastructure.repository.season_repository import SeasonRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository
from modules.tournaments.infrastructure.repository.tournament_repository import TournamentRepository


class TournamentsModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(TournamentRepository, to=TournamentRepository, scope=injector.singleton)
        binder.bind(
            TournamentQueryRepository, to=TournamentQueryRepository, scope=injector.singleton
        )
        binder.bind(CreateTournamentUseCase, to=CreateTournamentUseCase, scope=injector.singleton)
        binder.bind(ListTournamentsQuery, to=ListTournamentsQuery, scope=injector.singleton)
        binder.bind(GetTournamentQuery, to=GetTournamentQuery, scope=injector.singleton)
        binder.bind(SeasonRepository, to=SeasonRepository, scope=injector.singleton)
        binder.bind(SeasonQueryRepository, to=SeasonQueryRepository, scope=injector.singleton)
        binder.bind(CreateSeasonUseCase, to=CreateSeasonUseCase, scope=injector.singleton)
        binder.bind(ListSeasonsQuery, to=ListSeasonsQuery, scope=injector.singleton)
        binder.bind(GetSeasonQuery, to=GetSeasonQuery, scope=injector.singleton)
        binder.bind(PhaseRepository, to=PhaseRepository, scope=injector.singleton)
        binder.bind(PhaseQueryRepository, to=PhaseQueryRepository, scope=injector.singleton)
        binder.bind(CreatePhaseUseCase, to=CreatePhaseUseCase, scope=injector.singleton)
        binder.bind(ListPhasesQuery, to=ListPhasesQuery, scope=injector.singleton)
        binder.bind(GetPhaseQuery, to=GetPhaseQuery, scope=injector.singleton)
        binder.bind(GroupRepository, to=GroupRepository, scope=injector.singleton)
        binder.bind(GroupQueryRepository, to=GroupQueryRepository, scope=injector.singleton)
        binder.bind(CreateGroupUseCase, to=CreateGroupUseCase, scope=injector.singleton)
        binder.bind(ListGroupsQuery, to=ListGroupsQuery, scope=injector.singleton)
        binder.bind(GetGroupQuery, to=GetGroupQuery, scope=injector.singleton)
        binder.bind(GroupEntryRepository, to=GroupEntryRepository, scope=injector.singleton)
        binder.bind(
            GroupEntryQueryRepository, to=GroupEntryQueryRepository, scope=injector.singleton
        )
        binder.bind(CreateGroupEntryUseCase, to=CreateGroupEntryUseCase, scope=injector.singleton)
        binder.bind(ListGroupEntriesQuery, to=ListGroupEntriesQuery, scope=injector.singleton)
        binder.bind(GetGroupEntryQuery, to=GetGroupEntryQuery, scope=injector.singleton)
        binder.bind(FixtureRepository, to=FixtureRepository, scope=injector.singleton)
        binder.bind(FixtureQueryRepository, to=FixtureQueryRepository, scope=injector.singleton)
        binder.bind(CreateFixtureUseCase, to=CreateFixtureUseCase, scope=injector.singleton)
        binder.bind(ListFixturesQuery, to=ListFixturesQuery, scope=injector.singleton)
        binder.bind(GetFixtureQuery, to=GetFixtureQuery, scope=injector.singleton)
        binder.bind(
            CompetitionQueryRepository, to=CompetitionQueryRepository, scope=injector.singleton
        )
        binder.bind(SetPhaseStatusUseCase, to=SetPhaseStatusUseCase, scope=injector.singleton)
        binder.bind(GetSeasonStandingsQuery, to=GetSeasonStandingsQuery, scope=injector.singleton)
        binder.bind(GetSeasonBracketQuery, to=GetSeasonBracketQuery, scope=injector.singleton)
        binder.bind(ListSeasonFixturesQuery, to=ListSeasonFixturesQuery, scope=injector.singleton)
        binder.bind(StructureRepository, to=StructureRepository, scope=injector.singleton)
        binder.bind(BracketRepository, to=BracketRepository, scope=injector.singleton)
        binder.bind(AddSeasonTeamUseCase, to=AddSeasonTeamUseCase, scope=injector.singleton)
        binder.bind(RemoveSeasonTeamUseCase, to=RemoveSeasonTeamUseCase, scope=injector.singleton)
        binder.bind(UpdatePhaseUseCase, to=UpdatePhaseUseCase, scope=injector.singleton)
        binder.bind(UpdateGroupUseCase, to=UpdateGroupUseCase, scope=injector.singleton)
        binder.bind(UpdateFixtureUseCase, to=UpdateFixtureUseCase, scope=injector.singleton)
        binder.bind(DeletePhaseUseCase, to=DeletePhaseUseCase, scope=injector.singleton)
        binder.bind(DeleteGroupUseCase, to=DeleteGroupUseCase, scope=injector.singleton)
        binder.bind(DeleteFixtureUseCase, to=DeleteFixtureUseCase, scope=injector.singleton)
        binder.bind(DeleteGroupEntryUseCase, to=DeleteGroupEntryUseCase, scope=injector.singleton)
        binder.bind(SetGroupTieBreakUseCase, to=SetGroupTieBreakUseCase, scope=injector.singleton)
        binder.bind(GenerateBracketUseCase, to=GenerateBracketUseCase, scope=injector.singleton)
        binder.bind(AdvanceBracketUseCase, to=AdvanceBracketUseCase, scope=injector.singleton)
