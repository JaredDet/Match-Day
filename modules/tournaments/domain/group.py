from __future__ import annotations

import uuid

from django.db import models

from modules.tournaments.domain.phase import Phase, PhaseKind
from modules.tournaments.domain.validation import normalize_name
from modules.tournaments.errors import TournamentErrors


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.ForeignKey("tournaments.Phase", on_delete=models.PROTECT, related_name="groups")
    name = models.CharField(max_length=30)
    tie_break_order = models.JSONField(default=list, blank=True)

    @classmethod
    def create(cls, *, phase: Phase, name: str) -> Group:
        if phase.kind != PhaseKind.GROUPS:
            raise TournamentErrors.InvalidGroupPhase

        return cls(phase_id=phase.id, name=normalize_name(name, 30))

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(fields=["phase", "name"], name="unique_phase_group_name")
        ]
