from modules.matches.domain.shot import Shot


class ShotRepository:
    def save(self, shot: Shot) -> None:
        shot.save()
