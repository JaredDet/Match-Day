from modules.matches.domain.injury import Injury


class InjuryRepository:
    def save(self, injury: Injury) -> None:
        injury.save()
