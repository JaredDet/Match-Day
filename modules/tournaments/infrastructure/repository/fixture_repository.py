from uuid import UUID

from django.db import IntegrityError, transaction

from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.errors import TournamentErrors


class FixtureRepository:
    def get(self, fixture_id: UUID) -> Fixture | None:
        return Fixture.objects.filter(id=fixture_id).first()

    def get_for_update(self, fixture_id: UUID) -> Fixture | None:
        return Fixture.objects.select_for_update().filter(id=fixture_id).first()

    def save(self, entity: Fixture) -> None:
        try:
            with transaction.atomic():
                entity.save()
        except IntegrityError as error:
            if "unique" in str(error).lower():
                raise TournamentErrors.FixtureAlreadyExists from error

            raise
