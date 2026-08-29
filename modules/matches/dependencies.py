import injector

from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class MatchesModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.bind(MatchRepository, to=MatchRepository, scope=injector.singleton)
        binder.bind(CreateMatchUseCase, to=CreateMatchUseCase, scope=injector.singleton)
