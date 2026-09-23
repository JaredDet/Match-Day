from __future__ import annotations

import uuid
from datetime import date

from django.db import models
from django.db.models.functions import Lower

from core.constants import NAME_MAX_LENGTH
from core.text import normalize_whitespace
from modules.teams.errors import TeamErrors


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    head_coach_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        null=True,
        blank=True,
    )
    crest = models.ImageField(upload_to="teams/crests/", null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    stadium_name = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    founded_year = models.PositiveSmallIntegerField(null=True, blank=True)
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
    def create(
        cls,
        *,
        name: str,
        head_coach_name: str | None = None,
        crest=None,
        city: str | None = None,
        stadium_name: str | None = None,
        founded_year: int | None = None,
    ) -> Team:
        team = cls(
            name=cls._normalize_name(name),
            head_coach_name=cls._normalize_optional_name(head_coach_name),
        )
        team.update_profile(
            crest=crest,
            city=city,
            stadium_name=stadium_name,
            founded_year=founded_year,
        )
        return team

    def rename(self, name: str) -> None:
        self.name = self._normalize_name(name)

    def set_head_coach(self, head_coach_name: str | None) -> None:
        self.head_coach_name = self._normalize_optional_name(head_coach_name)

    def update_profile(
        self,
        *,
        crest=None,
        city: str | None = None,
        stadium_name: str | None = None,
        founded_year: int | None = None,
    ) -> None:
        if founded_year is not None and (
            not isinstance(founded_year, int)
            or isinstance(founded_year, bool)
            or not 1800 <= founded_year <= date.today().year
        ):
            raise TeamErrors.InvalidFoundedYear
        self.crest = crest
        self.city = self._normalize_optional_name(city)
        self.stadium_name = self._normalize_optional_name(stadium_name)
        self.founded_year = founded_year

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

    @staticmethod
    def _normalize_optional_name(name: str | None) -> str | None:
        normalized_name = normalize_whitespace(name)
        return normalized_name or None

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
            models.CheckConstraint(
                condition=models.Q(founded_year__isnull=True) | models.Q(founded_year__gte=1800),
                name="team_valid_founded_year",
            ),
        ]
