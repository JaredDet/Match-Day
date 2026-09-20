from uuid import UUID

from django.db import IntegrityError, transaction

from modules.tournaments.domain.tournament import Tournament
from modules.tournaments.errors import TournamentErrors


class TournamentRepository:
    def get(self, tournament_id: UUID) -> Tournament | None:
        return Tournament.objects.filter(id=tournament_id).first()

    def get_for_update(self, tournament_id: UUID) -> Tournament | None:
        return Tournament.objects.select_for_update().filter(id=tournament_id).first()

    def save(self, entity: Tournament) -> None:
        try:
            with transaction.atomic():
                entity.save()
        except IntegrityError as error:
            if "unique" in str(error).lower():
                raise TournamentErrors.AlreadyExists from error

            raise
