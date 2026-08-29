import uuid

from django.db import models

from modules.matches.domain.match_event import TeamSide


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
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    player_name = models.CharField(max_length=200)
    card_type = models.CharField(max_length=10, choices=CardType.choices)
    minute = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

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
                condition=models.Q(minute__gte=0, minute__lte=130),
                name="valid_card_minute",
            ),
            models.CheckConstraint(
                condition=~models.Q(player_name=""),
                name="card_player_name_not_empty",
            ),
        ]
