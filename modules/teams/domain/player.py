from __future__ import annotations

import uuid
from uuid import UUID

from django.db import models
from django.db.models.functions import Lower

from core.text import normalize_whitespace
from modules.teams.errors import TeamErrors


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="players",
    )
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, *, team_id: UUID, name: str) -> Player:
        return cls(team_id=team_id, name=cls._normalize_name(name))

    def rename(self, name: str) -> None:
        self.name = self._normalize_name(name)

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized_name = normalize_whitespace(name)
        if not normalized_name:
            raise TeamErrors.InvalidPlayerName
        return normalized_name

    class Meta:
        db_table = "players"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "team",
                name="unique_player_name_per_team",
            ),
            models.CheckConstraint(
                condition=~models.Q(name=""),
                name="player_name_not_empty",
            ),
        ]
