import uuid
from datetime import datetime

from django.db import models
from django.utils import timezone

from core.constants import NAME_MAX_LENGTH
from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors


class Goal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="goals",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="goals",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    player_name = models.CharField(max_length=NAME_MAX_LENGTH)
    minute = models.PositiveSmallIntegerField()
    disallowed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def disallow(self, disallowed_at: datetime | None = None) -> None:
        if self.disallowed_at is not None:
            raise MatchErrors.GoalAlreadyDisallowed
        self.disallowed_at = disallowed_at or timezone.now()

    class Meta:
        db_table = "match_goals"
        ordering = ["minute", "created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_goal_team_side",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    minute__gte=MIN_MATCH_MINUTE,
                    minute__lte=MAX_MATCH_MINUTE,
                ),
                name="valid_goal_minute",
            ),
            models.CheckConstraint(
                condition=~models.Q(player_name=""),
                name="goal_player_name_not_empty",
            ),
        ]
