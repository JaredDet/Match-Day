import uuid

from django.db import models

from modules.matches.domain.match_event import TeamSide


class Goal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="goals",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    player_name = models.CharField(max_length=200)
    minute = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "match_goals"
        ordering = ["minute", "created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_goal_team_side",
            ),
            models.CheckConstraint(
                condition=models.Q(minute__gte=0, minute__lte=130),
                name="valid_goal_minute",
            ),
            models.CheckConstraint(
                condition=~models.Q(player_name=""),
                name="goal_player_name_not_empty",
            ),
        ]
