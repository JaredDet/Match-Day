from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models

from core.text import normalize_whitespace
from modules.tournaments.constants import DEFAULT_MAX_TEAMS_PER_GROUP
from modules.tournaments.domain.validation import normalize_name
from modules.tournaments.errors import TournamentErrors


class Tournament(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    max_teams_per_group = models.PositiveSmallIntegerField(default=DEFAULT_MAX_TEAMS_PER_GROUP)

    def ensure_group_capacity(self, participant_count: int) -> None:
        if participant_count >= self.max_teams_per_group:
            raise TournamentErrors.GroupFull

    @classmethod
    def create(
        cls,
        *,
        slug: str,
        name: str,
        country: str,
        category: str,
        max_teams_per_group: int = DEFAULT_MAX_TEAMS_PER_GROUP,
    ) -> Tournament:
        if type(max_teams_per_group) is not int or not 1 <= max_teams_per_group <= 32767:
            raise TournamentErrors.InvalidGroupCapacity

        slug = slug.strip()

        try:
            validate_slug(slug)
        except ValidationError as error:
            raise TournamentErrors.InvalidSlug from error

        if not slug or len(slug) > 50:
            raise TournamentErrors.InvalidSlug

        country, category = normalize_whitespace(country), normalize_whitespace(category)

        if not country or not category or max(len(country), len(category)) > 100:
            raise TournamentErrors.InvalidMetadata

        return cls(
            slug=slug,
            name=normalize_name(name, 150),
            country=country,
            category=category,
            max_teams_per_group=max_teams_per_group,
        )

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(max_teams_per_group__gte=1),
                name="tournament_positive_group_capacity",
            )
        ]
