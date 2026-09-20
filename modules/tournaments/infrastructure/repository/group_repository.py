from uuid import UUID

from django.db import IntegrityError, transaction

from modules.tournaments.domain.group import Group
from modules.tournaments.errors import TournamentErrors


class GroupRepository:
    def get(self, group_id: UUID) -> Group | None:
        return Group.objects.filter(id=group_id).first()

    def get_for_update(self, group_id: UUID) -> Group | None:
        return Group.objects.select_for_update().filter(id=group_id).first()

    def save(self, entity: Group) -> None:
        try:
            with transaction.atomic():
                entity.save()
        except IntegrityError as error:
            if "unique" in str(error).lower():
                raise TournamentErrors.GroupAlreadyExists from error

            raise
