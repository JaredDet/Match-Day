import uuid
from datetime import datetime

from django.db import models
from django.utils import timezone

from core.constants import NAME_MAX_LENGTH
from modules.matches.constants import (
    FIRST_HALF_END_MINUTE,
    MAX_MATCH_MINUTE,
    MIN_MATCH_MINUTE,
    SECOND_HALF_START_MINUTE,
)
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.errors import MatchErrors


class CardType(models.TextChoices):
    YELLOW = "yellow"
    RED = "red"


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="cards",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="cards",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    player_name = models.CharField(max_length=NAME_MAX_LENGTH)
    card_type = models.CharField(max_length=10, choices=CardType.choices)
    period = models.CharField(max_length=20, choices=MatchPeriod.choices)
    minute = models.PositiveSmallIntegerField()
    added_minute = models.PositiveSmallIntegerField(default=0)
    rescinded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def rescind(self, rescinded_at: datetime | None = None) -> None:
        if self.rescinded_at is not None:
            raise MatchErrors.CardAlreadyRescinded
        self.rescinded_at = rescinded_at or timezone.now()

    class Meta:
        db_table = "match_cards"
        ordering = ["minute", "created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_card_team_side",
            ),
            models.CheckConstraint(
                condition=models.Q(card_type__in=CardType.values),
                name="valid_card_type",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    minute__gte=MIN_MATCH_MINUTE,
                    minute__lte=MAX_MATCH_MINUTE,
                ),
                name="valid_card_minute",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        period=MatchPeriod.FIRST_HALF,
                        minute__gte=MIN_MATCH_MINUTE,
                        minute__lte=FIRST_HALF_END_MINUTE,
                    )
                    | models.Q(
                        period=MatchPeriod.SECOND_HALF,
                        minute__gte=SECOND_HALF_START_MINUTE,
                        minute__lte=MAX_MATCH_MINUTE,
                    )
                ),
                name="valid_card_period_minute",
            ),
            models.CheckConstraint(
                condition=models.Q(added_minute=0)
                | models.Q(
                    period=MatchPeriod.FIRST_HALF,
                    minute=FIRST_HALF_END_MINUTE,
                )
                | models.Q(
                    period=MatchPeriod.SECOND_HALF,
                    minute=MAX_MATCH_MINUTE,
                ),
                name="valid_card_added_minute",
            ),
            models.CheckConstraint(
                condition=~models.Q(player_name=""),
                name="card_player_name_not_empty",
            ),
        ]
