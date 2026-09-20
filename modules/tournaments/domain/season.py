from __future__ import annotations

import uuid
from uuid import UUID

from django.db import models

from modules.tournaments.domain.validation import normalize_name


class Season(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey(
        "tournaments.Tournament", on_delete=models.PROTECT, related_name="seasons"
    )
    name = models.CharField(max_length=30)
    teams = models.ManyToManyField("teams.Team", blank=True, related_name="tournament_seasons")

    @classmethod
    def create(cls, *, tournament_id: UUID, name: str) -> Season:
        return cls(tournament_id=tournament_id, name=normalize_name(name, 30))

    class Meta:
        ordering = ["-name", "id"]
        constraints = [
            models.UniqueConstraint(fields=["tournament", "name"], name="unique_tournament_season")
        ]
