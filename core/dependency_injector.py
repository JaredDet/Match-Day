import injector

from core.dependencies import CoreModule
from modules.matches.dependencies import MatchesModule
from modules.news.dependencies import NewsModule
from modules.recommendations.dependencies import RecommendationsModule
from modules.teams.dependencies import TeamsModule
from modules.tournaments.dependencies import TournamentsModule

injector_instance = injector.Injector(
    [
        CoreModule(),
        TeamsModule(),
        MatchesModule(),
        NewsModule(),
        TournamentsModule(),
        RecommendationsModule(),
    ],
    auto_bind=False,
)
