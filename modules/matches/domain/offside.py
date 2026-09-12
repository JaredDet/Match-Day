import uuid

from django.db import models

from core.constants import NAME_MAX_LENGTH
from modules.matches.domain.match_event import (
    MatchPeriod,
    TeamSide,
    timed_match_event_constraints,
)


class Offside(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="offsides",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="offsides",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    player_name = models.CharField(max_length=NAME_MAX_LENGTH)
    period = models.CharField(max_length=25, choices=MatchPeriod.choices)
    minute = models.PositiveSmallIntegerField()
    added_minute = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "match_offsides"
        ordering = ["minute", "added_minute", "created_at"]
        constraints = [*timed_match_event_constraints("offside")]
