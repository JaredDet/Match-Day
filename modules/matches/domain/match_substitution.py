import uuid

from django.db import models

from modules.matches.constants import (
    FIRST_HALF_END_MINUTE,
    MAX_MATCH_MINUTE,
    MIN_MATCH_MINUTE,
    SECOND_HALF_START_MINUTE,
)
from modules.matches.domain.match_event import MatchPeriod, TeamSide, validate_match_event
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
    period = models.CharField(max_length=20, choices=MatchPeriod.choices)
    minute = models.PositiveSmallIntegerField()
    added_minute = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(
        cls,
        *,
        match,
        player_out,
        player_in,
        minute: int,
        added_minute: int = 0,
    ) -> "MatchSubstitution":
        if (
            player_out.id == player_in.id
            or player_out.match_id != match.id
            or player_in.match_id != match.id
        ):
            raise MatchErrors.InvalidSubstitutionPlayers
        if player_out.team_side != player_in.team_side:
            raise MatchErrors.InvalidSubstitutionPlayers
        if player_out.is_sent_off or player_in.is_sent_off:
            raise MatchErrors.PlayerSentOff
        if not player_out.is_on_field:
            raise MatchErrors.InvalidOutgoingPlayer
        if player_in.role != MatchSquadRole.SUBSTITUTE or player_in.is_on_field:
            raise MatchErrors.InvalidSubstitutePlayer
        team_side = TeamSide(player_out.team_side)
        try:
            period = MatchPeriod(match.current_period)
        except (TypeError, ValueError):
            raise MatchErrors.InvalidPeriod from None
        validate_match_event(team_side, period, minute, added_minute)
        match.ensure_event_time_reached(period, minute, added_minute)
        player_out.leave_field()
        player_in.enter_field()
        return cls(
            match=match,
            player_out=player_out,
            player_in=player_in,
            team_side=team_side,
            period=period,
            minute=minute,
            added_minute=added_minute,
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
                name="valid_substitution_period_minute",
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
                name="valid_substitution_added_minute",
            ),
            models.CheckConstraint(
                condition=~models.Q(player_out=models.F("player_in")),
                name="substitution_players_are_different",
            ),
        ]
