import injector

from modules.recommendations.application.commands.clear_navigation_history_use_case import (
    ClearNavigationHistoryUseCase,
)
from modules.recommendations.application.commands.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from modules.recommendations.application.commands.process_recommendations_use_case import (
    ProcessRecommendationsUseCase,
)
from modules.recommendations.application.commands.purge_navigation_history_use_case import (
    PurgeNavigationHistoryUseCase,
)
from modules.recommendations.application.commands.record_active_time_use_case import (
    RecordActiveTimeUseCase,
)
from modules.recommendations.application.commands.record_navigation_use_case import (
    RecordNavigationUseCase,
)
from modules.recommendations.application.queries.get_recommendations_query import (
    GetRecommendationsQuery,
)
from modules.recommendations.infrastructure.query_repository.content_query_repository import (
    ContentQueryRepository,
)
from modules.recommendations.infrastructure.query_repository.recommendation_query_repository import (
    RecommendationQueryRepository,
)
from modules.recommendations.infrastructure.repository.navigation_repository import (
    NavigationRepository,
)
from modules.recommendations.infrastructure.repository.recommendation_repository import (
    RecommendationRepository,
)


class RecommendationsModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(
            RecommendationQueryRepository,
            to=RecommendationQueryRepository,
            scope=injector.singleton,
        )
        binder.bind(NavigationRepository, to=NavigationRepository, scope=injector.singleton)
        binder.bind(RecommendationRepository, to=RecommendationRepository, scope=injector.singleton)
        binder.bind(ContentQueryRepository, to=ContentQueryRepository, scope=injector.singleton)
        binder.bind(RecordNavigationUseCase, to=RecordNavigationUseCase, scope=injector.singleton)
        binder.bind(RecordActiveTimeUseCase, to=RecordActiveTimeUseCase, scope=injector.singleton)
        binder.bind(
            ClearNavigationHistoryUseCase,
            to=ClearNavigationHistoryUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            PurgeNavigationHistoryUseCase,
            to=PurgeNavigationHistoryUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            GenerateRecommendationsUseCase,
            to=GenerateRecommendationsUseCase,
            scope=injector.singleton,
        )
        binder.bind(
            ProcessRecommendationsUseCase,
            to=ProcessRecommendationsUseCase,
            scope=injector.singleton,
        )
        binder.bind(GetRecommendationsQuery, to=GetRecommendationsQuery, scope=injector.singleton)
