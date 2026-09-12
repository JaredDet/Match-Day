from modules.matches.domain.corner_kick import CornerKick


class CornerKickRepository:
    def save(self, corner_kick: CornerKick) -> None:
        corner_kick.save()
