import injector

from core.dependencies import CoreModule
from modules.matches.dependencies import MatchesModule
from modules.news.dependencies import NewsModule
from modules.teams.dependencies import TeamsModule

injector_instance = injector.Injector(
    [CoreModule(), TeamsModule(), MatchesModule(), NewsModule()],
    auto_bind=False,
)
