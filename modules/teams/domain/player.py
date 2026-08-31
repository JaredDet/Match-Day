from __future__ import annotations

import uuid
from uuid import UUID

from django.db import models
from django.db.models.functions import Lower

from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER, NAME_MAX_LENGTH
from core.text import normalize_whitespace
from modules.teams.errors import TeamErrors

PLAYER_POSITION_MAX_LENGTH = 25


class PlayerPosition(models.TextChoices):
    GOALKEEPER = "goalkeeper"
    RIGHT_BACK = "right_back"
    CENTER_BACK = "center_back"
    LEFT_BACK = "left_back"
    SWEEPER = "sweeper"
    RIGHT_WING_BACK = "right_wing_back"
    LEFT_WING_BACK = "left_wing_back"
    DEFENSIVE_MIDFIELDER = "defensive_midfielder"
    CENTRAL_MIDFIELDER = "central_midfielder"
    ATTACKING_MIDFIELDER = "attacking_midfielder"
    RIGHT_MIDFIELDER = "right_midfielder"
    LEFT_MIDFIELDER = "left_midfielder"
    RIGHT_WINGER = "right_winger"
    LEFT_WINGER = "left_winger"
    SECOND_STRIKER = "second_striker"
    CENTER_FORWARD = "center_forward"


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="players",
    )
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    preferred_position = models.CharField(
        max_length=PLAYER_POSITION_MAX_LENGTH,
        choices=PlayerPosition.choices,
        null=True,
        blank=True,
    )
    preferred_shirt_number = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(
        cls,
        *,
        team_id: UUID,
        name: str,
        preferred_position: PlayerPosition | None = None,
        preferred_shirt_number: int | None = None,
    ) -> Player:
        player = cls(team_id=team_id, name=cls._normalize_name(name))
        player.update_profile(
            preferred_position=preferred_position,
            preferred_shirt_number=preferred_shirt_number,
        )
        return player

    def rename(self, name: str) -> None:
        self.name = self._normalize_name(name)

    def update_profile(
        self,
        *,
        preferred_position: PlayerPosition | None,
        preferred_shirt_number: int | None,
    ) -> None:
        if preferred_position is not None and not isinstance(
            preferred_position, PlayerPosition
        ):
            raise TeamErrors.InvalidPlayerPosition
        if preferred_shirt_number is not None and (
            not isinstance(preferred_shirt_number, int)
            or isinstance(preferred_shirt_number, bool)
            or not MIN_SHIRT_NUMBER <= preferred_shirt_number <= MAX_SHIRT_NUMBER
        ):
            raise TeamErrors.InvalidPlayerShirtNumber
        self.preferred_position = preferred_position
        self.preferred_shirt_number = preferred_shirt_number

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
            models.CheckConstraint(
                condition=models.Q(preferred_position__isnull=True)
                | models.Q(preferred_position__in=PlayerPosition.values),
                name="valid_player_preferred_position",
            ),
            models.CheckConstraint(
                condition=models.Q(preferred_shirt_number__isnull=True)
                | models.Q(
                    preferred_shirt_number__gte=MIN_SHIRT_NUMBER,
                    preferred_shirt_number__lte=MAX_SHIRT_NUMBER,
                ),
                name="valid_player_preferred_shirt_number",
            ),
            models.UniqueConstraint(
                fields=["team", "preferred_shirt_number"],
                condition=models.Q(preferred_shirt_number__isnull=False),
                name="unique_player_preferred_shirt_per_team",
            ),
        ]
