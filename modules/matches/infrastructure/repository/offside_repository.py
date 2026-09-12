from modules.matches.domain.offside import Offside


class OffsideRepository:
    def save(self, offside: Offside) -> None:
        offside.save()
