from uuid import UUID

from django.db import IntegrityError, transaction

from modules.tournaments.domain.season import Season
from modules.tournaments.errors import TournamentErrors


class SeasonRepository:
    def get(self, season_id: UUID) -> Season | None:
        return Season.objects.filter(id=season_id).first()

    def get_for_update(self, season_id: UUID) -> Season | None:
        return Season.objects.select_for_update().filter(id=season_id).first()

    def save(self, entity: Season) -> None:
        try:
            with transaction.atomic():
                entity.save()
        except IntegrityError as error:
            if "unique" in str(error).lower():
                raise TournamentErrors.SeasonAlreadyExists from error

            raise

    def set_teams(self, season: Season, team_ids: list[UUID]) -> None:
        season.teams.set(team_ids)

    def team_ids(self, season_id: UUID) -> set[UUID]:
        return set(Season.objects.get(id=season_id).teams.values_list("id", flat=True))
