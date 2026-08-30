import injector

from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.application.commands.update_match_details_use_case import (
    UpdateMatchDetailsUseCase,
)
from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.list_matches_query import ListMatchesQuery
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)
from modules.matches.infrastructure.repository.card_repository import CardRepository
from modules.matches.infrastructure.repository.goal_repository import GoalRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class MatchesModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(MatchRepository, to=MatchRepository, scope=injector.singleton)
        binder.bind(CardRepository, to=CardRepository, scope=injector.singleton)
        binder.bind(GoalRepository, to=GoalRepository, scope=injector.singleton)
        binder.bind(MatchQueryRepository, to=MatchQueryRepository, scope=injector.singleton)
        binder.bind(CreateMatchUseCase, to=CreateMatchUseCase, scope=injector.singleton)
        binder.bind(FinishMatchUseCase, to=FinishMatchUseCase, scope=injector.singleton)
        binder.bind(RegisterCardUseCase, to=RegisterCardUseCase, scope=injector.singleton)
        binder.bind(RegisterGoalUseCase, to=RegisterGoalUseCase, scope=injector.singleton)
        binder.bind(StartMatchUseCase, to=StartMatchUseCase, scope=injector.singleton)
        binder.bind(
            UpdateMatchDetailsUseCase,
            to=UpdateMatchDetailsUseCase,
            scope=injector.singleton,
        )
        binder.bind(DisallowGoalUseCase, to=DisallowGoalUseCase, scope=injector.singleton)
        binder.bind(RescindCardUseCase, to=RescindCardUseCase, scope=injector.singleton)
        binder.bind(GetMatchQuery, to=GetMatchQuery, scope=injector.singleton)
        binder.bind(ListMatchesQuery, to=ListMatchesQuery, scope=injector.singleton)
