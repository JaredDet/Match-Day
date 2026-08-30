import uuid

from django.db import models

from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors


class MatchLineupPlayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="lineup_players",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="match_lineups",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    shirt_number = models.PositiveSmallIntegerField()
    is_captain = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(
        cls,
        *,
        match,
        player,
        team_side: TeamSide,
        shirt_number: int,
        is_captain: bool = False,
    ) -> "MatchLineupPlayer":
        if not isinstance(team_side, TeamSide):
            raise MatchErrors.InvalidTeamSide
        if not isinstance(shirt_number, int) or isinstance(shirt_number, bool):
            raise MatchErrors.InvalidShirtNumber
        if not 1 <= shirt_number <= 99:
            raise MatchErrors.InvalidShirtNumber
        return cls(
            match=match,
            player=player,
            team_side=team_side,
            shirt_number=shirt_number,
            is_captain=is_captain,
        )

    class Meta:
        db_table = "match_lineup_players"
        ordering = ["team_side", "shirt_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["match", "player"],
                name="unique_player_per_match_lineup",
            ),
            models.UniqueConstraint(
                fields=["match", "team_side", "shirt_number"],
                name="unique_shirt_per_match_team",
            ),
            models.UniqueConstraint(
                fields=["match", "team_side"],
                condition=models.Q(is_captain=True),
                name="unique_captain_per_match_team",
            ),
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_lineup_player_team_side",
            ),
            models.CheckConstraint(
                condition=models.Q(shirt_number__gte=1, shirt_number__lte=99),
                name="valid_lineup_shirt_number",
            ),
        ]
