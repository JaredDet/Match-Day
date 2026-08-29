import injector

from core.dependencies import CoreModule
from modules.matches.dependencies import MatchesModule

injector_instance = injector.Injector(
    [CoreModule(), MatchesModule()],
    auto_bind=False,
)
