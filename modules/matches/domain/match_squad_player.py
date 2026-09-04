import uuid

from django.db import models

from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors


class MatchSquadRole(models.TextChoices):
    STARTER = "starter"
    SUBSTITUTE = "substitute"


class SentOffReason(models.TextChoices):
    DIRECT_RED = "direct_red"
    SECOND_YELLOW = "second_yellow"


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
    is_on_field = models.BooleanField(default=False)
    is_sent_off = models.BooleanField(default=False)
    sent_off_reason = models.CharField(
        max_length=20,
        choices=SentOffReason.choices,
        null=True,
        blank=True,
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
            is_on_field=role == MatchSquadRole.STARTER,
            is_captain=is_captain,
        )

    def enter_field(self) -> None:
        if self.is_sent_off:
            raise MatchErrors.PlayerSentOff

        if self.role != MatchSquadRole.SUBSTITUTE or self.is_on_field:
            raise MatchErrors.InvalidSubstitutePlayer

        self.is_on_field = True

    def leave_field(self) -> None:
        if self.is_sent_off:
            raise MatchErrors.PlayerSentOff

        if not self.is_on_field:
            raise MatchErrors.InvalidOutgoingPlayer

        self.is_on_field = False

    def send_off(self, reason: SentOffReason) -> None:
        if not isinstance(reason, SentOffReason):
            raise MatchErrors.InvalidSentOffReason

        if self.is_sent_off:
            raise MatchErrors.PlayerSentOff

        if not self.is_on_field:
            raise MatchErrors.PlayerNotOnField

        self.is_sent_off = True
        self.sent_off_reason = reason
        self.is_on_field = False

    def reinstate(self) -> None:
        if not self.is_sent_off:
            return

        self.is_sent_off = False
        self.sent_off_reason = None
        self.is_on_field = True

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
            models.CheckConstraint(
                condition=models.Q(is_sent_off=False) | models.Q(is_on_field=False),
                name="sent_off_player_must_be_off_field",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(is_sent_off=False, sent_off_reason__isnull=True)
                    | models.Q(
                        is_sent_off=True,
                        sent_off_reason__in=SentOffReason.values,
                    )
                ),
                name="valid_player_sent_off_reason",
            ),
        ]
