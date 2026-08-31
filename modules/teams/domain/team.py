from __future__ import annotations

import uuid

from django.db import models
from django.db.models.functions import Lower

from core.constants import NAME_MAX_LENGTH
from core.text import normalize_whitespace
from modules.teams.errors import TeamErrors


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    captain = models.ForeignKey(
        "teams.Player",
        on_delete=models.SET_NULL,
        related_name="captained_teams",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, *, name: str) -> Team:
        return cls(name=cls._normalize_name(name))

    def rename(self, name: str) -> None:
        self.name = self._normalize_name(name)

    def assign_captain(self, player) -> None:
        if player.team_id != self.id:
            raise TeamErrors.InvalidCaptain
        self.captain = player

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized_name = normalize_whitespace(name)
        if not normalized_name:
            raise TeamErrors.InvalidName
        return normalized_name

    class Meta:
        db_table = "teams"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_team_name_case_insensitive",
            ),
            models.CheckConstraint(
                condition=~models.Q(name=""),
                name="team_name_not_empty",
            ),
        ]
