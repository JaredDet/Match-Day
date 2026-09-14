import injector

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
from modules.matches.application.commands.update_match_details_use_case import (
    UpdateMatchDetailsUseCase,
)
from modules.matches.application.commands.update_match_possession_use_case import (
    UpdateMatchPossessionUseCase,
)
from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.list_matches_query import ListMatchesQuery
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)
from modules.matches.infrastructure.realtime.match_clock_publisher import MatchClockPublisher
from modules.matches.infrastructure.repository.card_repository import CardRepository
from modules.matches.infrastructure.repository.corner_kick_repository import (
    CornerKickRepository,
)
from modules.matches.infrastructure.repository.foul_repository import FoulRepository
from modules.matches.infrastructure.repository.goal_repository import GoalRepository
from modules.matches.infrastructure.repository.injury_repository import InjuryRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.matches.infrastructure.repository.match_substitution_repository import (
    MatchSubstitutionRepository,
)
from modules.matches.infrastructure.repository.offside_repository import OffsideRepository
from modules.matches.infrastructure.repository.penalty_attempt_repository import (
    PenaltyAttemptRepository,
)
from modules.matches.infrastructure.repository.penalty_shootout_repository import (
    PenaltyShootoutRepository,
)
from modules.matches.infrastructure.repository.shot_repository import ShotRepository
from modules.matches.infrastructure.repository.var_review_repository import VarReviewRepository


class MatchesModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(MatchRepository, to=MatchRepository, scope=injector.singleton)
        binder.bind(MatchClockPublisher, to=MatchClockPublisher, scope=injector.singleton)
        binder.bind(MatchSquadRepository, to=MatchSquadRepository, scope=injector.singleton)
        binder.bind(
            MatchSubstitutionRepository,
            to=MatchSubstitutionRepository,
            scope=injector.singleton,
        )
        binder.bind(CardRepository, to=CardRepository, scope=injector.singleton)
        binder.bind(CornerKickRepository, to=CornerKickRepository, scope=injector.singleton)
        binder.bind(FoulRepository, to=FoulRepository, scope=injector.singleton)
        binder.bind(GoalRepository, to=GoalRepository, scope=injector.singleton)
        binder.bind(InjuryRepository, to=InjuryRepository, scope=injector.singleton)
        binder.bind(OffsideRepository, to=OffsideRepository, scope=injector.singleton)
        binder.bind(ShotRepository, to=ShotRepository, scope=injector.singleton)
        binder.bind(
            PenaltyAttemptRepository,
            to=PenaltyAttemptRepository,
            scope=injector.singleton,
        )
        binder.bind(VarReviewRepository, to=VarReviewRepository, scope=injector.singleton)
        binder.bind(
            PenaltyShootoutRepository,
            to=PenaltyShootoutRepository,
            scope=injector.singleton,
        )
        binder.bind(MatchQueryRepository, to=MatchQueryRepository, scope=injector.singleton)
        binder.bind(CreateMatchUseCase, to=CreateMatchUseCase, scope=injector.singleton)
        binder.bind(FinishMatchUseCase, to=FinishMatchUseCase, scope=injector.singleton)
        binder.bind(EndMatchPeriodUseCase, to=EndMatchPeriodUseCase, scope=injector.singleton)
        binder.bind(RegisterCardUseCase, to=RegisterCardUseCase, scope=injector.singleton)
        binder.bind(
            RegisterCornerKickUseCase,
            to=RegisterCornerKickUseCase,
            scope=injector.singleton,
        )
        binder.bind(RegisterFoulUseCase, to=RegisterFoulUseCase, scope=injector.singleton)
        binder.bind(RegisterGoalUseCase, to=RegisterGoalUseCase, scope=injector.singleton)
        binder.bind(RegisterInjuryUseCase, to=RegisterInjuryUseCase, scope=injector.singleton)
        binder.bind(RegisterOffsideUseCase, to=RegisterOffsideUseCase, scope=injector.singleton)
        binder.bind(RegisterShotUseCase, to=RegisterShotUseCase, scope=injector.singleton)
        binder.bind(
            RegisterPenaltyAttemptUseCase,
            to=RegisterPenaltyAttemptUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            RegisterVarReviewUseCase,
            to=RegisterVarReviewUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            ReducePenaltyShootoutParticipantsUseCase,
            to=ReducePenaltyShootoutParticipantsUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            StartPenaltyShootoutUseCase,
            to=StartPenaltyShootoutUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            RegisterPenaltyShootoutKickUseCase,
            to=RegisterPenaltyShootoutKickUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            FinishPenaltyShootoutUseCase,
            to=FinishPenaltyShootoutUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            RegisterSubstitutionUseCase,
            to=RegisterSubstitutionUseCase,
            scope=injector.singleton,
        )
        binder.bind(StartMatchUseCase, to=StartMatchUseCase, scope=injector.singleton)
        binder.bind(StartMatchPeriodUseCase, to=StartMatchPeriodUseCase, scope=injector.singleton)
        binder.bind(
            SetMatchPeriodAddedTimeUseCase,
            to=SetMatchPeriodAddedTimeUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            SynchronizeMatchClocksUseCase,
            to=SynchronizeMatchClocksUseCase,
            scope=injector.singleton,
        )
        binder.bind(SetMatchLineupUseCase, to=SetMatchLineupUseCase, scope=injector.singleton)
        binder.bind(
            UpdateMatchDetailsUseCase,
            to=UpdateMatchDetailsUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            UpdateMatchPossessionUseCase,
            to=UpdateMatchPossessionUseCase,
            scope=injector.singleton,
        )
        binder.bind(DisallowGoalUseCase, to=DisallowGoalUseCase, scope=injector.singleton)
        binder.bind(RescindCardUseCase, to=RescindCardUseCase, scope=injector.singleton)
        binder.bind(GetMatchQuery, to=GetMatchQuery, scope=injector.singleton)
        binder.bind(ListMatchesQuery, to=ListMatchesQuery, scope=injector.singleton)
