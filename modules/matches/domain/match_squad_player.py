import uuid

from django.db import models

from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors


class MatchSquadRole(models.TextChoices):
    STARTER = "starter"
    SUBSTITUTE = "substitute"


class MatchSquadPlayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="squad_players",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="match_squads",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    shirt_number = models.PositiveSmallIntegerField()
    role = models.CharField(
        max_length=10,
        choices=MatchSquadRole.choices,
        default=MatchSquadRole.STARTER,
    )
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
        role: MatchSquadRole = MatchSquadRole.STARTER,
        is_captain: bool = False,
    ) -> "MatchSquadPlayer":
        if not isinstance(team_side, TeamSide):
            raise MatchErrors.InvalidTeamSide
        if not isinstance(shirt_number, int) or isinstance(shirt_number, bool):
            raise MatchErrors.InvalidShirtNumber
        if not MIN_SHIRT_NUMBER <= shirt_number <= MAX_SHIRT_NUMBER:
            raise MatchErrors.InvalidShirtNumber
        if not isinstance(role, MatchSquadRole):
            raise MatchErrors.InvalidSquadRole
        if is_captain and role != MatchSquadRole.STARTER:
            raise MatchErrors.InvalidLineupCaptain
        return cls(
            match=match,
            player=player,
            team_side=team_side,
            shirt_number=shirt_number,
            role=role,
            is_captain=is_captain,
        )

    class Meta:
        db_table = "match_squad_players"
        ordering = ["team_side", "shirt_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["match", "player"],
                name="unique_player_per_match_squad",
            ),
            models.UniqueConstraint(
                fields=["match", "team_side", "shirt_number"],
                name="unique_squad_shirt_per_match_team",
            ),
            models.UniqueConstraint(
                fields=["match", "team_side"],
                condition=models.Q(is_captain=True),
                name="unique_squad_captain_per_match_team",
            ),
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_squad_player_team_side",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    shirt_number__gte=MIN_SHIRT_NUMBER,
                    shirt_number__lte=MAX_SHIRT_NUMBER,
                ),
                name="valid_squad_shirt_number",
            ),
            models.CheckConstraint(
                condition=models.Q(role__in=MatchSquadRole.values),
                name="valid_match_squad_role",
            ),
            models.CheckConstraint(
                condition=models.Q(is_captain=False)
                | models.Q(role=MatchSquadRole.STARTER),
                name="match_captain_must_be_starter",
            ),
        ]
