from __future__ import annotations

import uuid
from uuid import UUID

from django.db import models

from modules.tournaments.domain.group import Group
from modules.tournaments.errors import TournamentErrors


class GroupEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey("tournaments.Group", on_delete=models.PROTECT, related_name="entries")
    team = models.ForeignKey("teams.Team", on_delete=models.PROTECT)
    phase = models.ForeignKey("tournaments.Phase", on_delete=models.PROTECT, editable=False)

    @classmethod
    def create(cls, *, group: Group, team_id: UUID, registered_team_ids: set[UUID]) -> GroupEntry:
        if team_id not in registered_team_ids:
            raise TournamentErrors.TeamNotRegistered

        return cls(group_id=group.id, phase_id=group.phase_id, team_id=team_id)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["phase", "team"], name="unique_team_per_group_phase")
        ]
