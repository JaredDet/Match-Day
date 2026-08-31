import uuid

from django.db import models

from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.domain.match_event import TeamSide, validate_match_event
from modules.matches.domain.match_squad_player import MatchSquadRole
from modules.matches.errors import MatchErrors


class MatchSubstitution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="substitutions",
    )
    player_out = models.ForeignKey(
        "matches.MatchSquadPlayer",
        on_delete=models.PROTECT,
        related_name="substitutions_out",
    )
    player_in = models.ForeignKey(
        "matches.MatchSquadPlayer",
        on_delete=models.PROTECT,
        related_name="substitutions_in",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    minute = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(
        cls,
        *,
        match,
        player_out,
        player_in,
        minute: int,
    ) -> "MatchSubstitution":
        if (
            player_out.id == player_in.id
            or player_out.match_id != match.id
            or player_in.match_id != match.id
        ):
            raise MatchErrors.InvalidSubstitutionPlayers
        if player_out.team_side != player_in.team_side:
            raise MatchErrors.InvalidSubstitutionPlayers
        if not player_out.is_on_field:
            raise MatchErrors.InvalidOutgoingPlayer
        if player_in.role != MatchSquadRole.SUBSTITUTE or player_in.is_on_field:
            raise MatchErrors.InvalidSubstitutePlayer
        team_side = TeamSide(player_out.team_side)
        validate_match_event(team_side, minute)
        player_out.leave_field()
        player_in.enter_field()
        return cls(
            match=match,
            player_out=player_out,
            player_in=player_in,
            team_side=team_side,
            minute=minute,
        )

    class Meta:
        db_table = "match_substitutions"
        ordering = ["minute", "created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_substitution_team_side",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    minute__gte=MIN_MATCH_MINUTE,
                    minute__lte=MAX_MATCH_MINUTE,
                ),
                name="valid_substitution_minute",
            ),
            models.CheckConstraint(
                condition=~models.Q(player_out=models.F("player_in")),
                name="substitution_players_are_different",
            ),
        ]
