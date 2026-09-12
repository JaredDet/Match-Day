from modules.matches.domain.foul import Foul


class FoulRepository:
    def save(self, foul: Foul) -> None:
        foul.save()
