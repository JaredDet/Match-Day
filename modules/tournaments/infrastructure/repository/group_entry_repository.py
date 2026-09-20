from uuid import UUID

from django.db import IntegrityError, transaction

from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.errors import TournamentErrors


class GroupEntryRepository:
    def get(self, group_entry_id: UUID) -> GroupEntry | None:
        return GroupEntry.objects.filter(id=group_entry_id).first()

    def get_for_update(self, group_entry_id: UUID) -> GroupEntry | None:
        return GroupEntry.objects.select_for_update().filter(id=group_entry_id).first()

    def save(self, entity: GroupEntry) -> None:
        try:
            with transaction.atomic():
                entity.save()
        except IntegrityError as error:
            if "unique" in str(error).lower():
                raise TournamentErrors.GroupEntryAlreadyExists from error

            raise

    def team_ids(self, group_id: UUID) -> set[UUID]:
        return set(GroupEntry.objects.filter(group_id=group_id).values_list("team_id", flat=True))

    def exists_in_phase(self, phase_id: UUID, team_id: UUID) -> bool:
        return GroupEntry.objects.filter(phase_id=phase_id, team_id=team_id).exists()

    def count_by_group(self, group_id: UUID) -> int:
        return GroupEntry.objects.filter(group_id=group_id).count()
