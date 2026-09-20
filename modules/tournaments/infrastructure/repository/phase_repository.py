from uuid import UUID

from django.db import IntegrityError, transaction

from modules.tournaments.domain.phase import Phase
from modules.tournaments.errors import TournamentErrors


class PhaseRepository:
    def get(self, phase_id: UUID) -> Phase | None:
        return Phase.objects.filter(id=phase_id).first()

    def get_for_update(self, phase_id: UUID) -> Phase | None:
        return Phase.objects.select_for_update().filter(id=phase_id).first()

    def save(self, entity: Phase) -> None:
        try:
            with transaction.atomic():
                entity.save()
        except IntegrityError as error:
            if "unique" in str(error).lower():
                raise TournamentErrors.PhaseAlreadyExists from error

            raise
