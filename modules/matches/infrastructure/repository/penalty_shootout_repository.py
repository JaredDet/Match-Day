from uuid import UUID

from modules.matches.domain.penalty_shootout import PenaltyShootout, PenaltyShootoutKick


class PenaltyShootoutRepository:
    def exists(self, match_id: UUID) -> bool:
        return PenaltyShootout.objects.filter(match_id=match_id).exists()

    def get_for_update(self, match_id: UUID) -> PenaltyShootout | None:
        return PenaltyShootout.objects.select_for_update().filter(match_id=match_id).first()

    def next_sequence_number(self, shootout_id: UUID) -> int:
        return PenaltyShootoutKick.objects.filter(shootout_id=shootout_id).count() + 1

    def save(self, shootout: PenaltyShootout) -> None:
        shootout.save()

    def save_kick(self, kick: PenaltyShootoutKick) -> None:
        kick.save()
