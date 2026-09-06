import uuid
from datetime import datetime

from django.db import models
from django.utils import timezone

from core.constants import NAME_MAX_LENGTH
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors


class PenaltyShootoutStatus(models.TextChoices):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class PenaltyKickOutcome(models.TextChoices):
    SCORED = "scored"
    MISSED = "missed"


class PenaltyShootout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.OneToOneField(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="penalty_shootout",
    )
    status = models.CharField(
        max_length=20,
        choices=PenaltyShootoutStatus.choices,
        default=PenaltyShootoutStatus.IN_PROGRESS,
    )
    home_score = models.PositiveSmallIntegerField(default=0)
    away_score = models.PositiveSmallIntegerField(default=0)
    winner_team_side = models.CharField(
        max_length=10,
        choices=TeamSide.choices,
        null=True,
        blank=True,
    )
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def start(cls, *, match) -> "PenaltyShootout":
        match.ensure_penalty_shootout_can_start()

        return cls(match=match)

    def record_kick(self, team_side: TeamSide, outcome: PenaltyKickOutcome) -> None:
        if self.status != PenaltyShootoutStatus.IN_PROGRESS:
            raise MatchErrors.PenaltyShootoutAlreadyFinished

        if not isinstance(team_side, TeamSide):
            raise MatchErrors.InvalidTeamSide

        if not isinstance(outcome, PenaltyKickOutcome):
            raise MatchErrors.InvalidPenaltyKickOutcome

        if outcome == PenaltyKickOutcome.SCORED:
            if team_side == TeamSide.HOME:
                self.home_score += 1
            else:
                self.away_score += 1

    def finish(self, finished_at: datetime | None = None) -> None:
        if self.status != PenaltyShootoutStatus.IN_PROGRESS:
            raise MatchErrors.PenaltyShootoutAlreadyFinished

        if self.home_score == self.away_score:
            raise MatchErrors.PenaltyShootoutIsTied

        self.status = PenaltyShootoutStatus.FINISHED
        self.winner_team_side = (
            TeamSide.HOME if self.home_score > self.away_score else TeamSide.AWAY
        )
        self.finished_at = finished_at or timezone.now()

    class Meta:
        db_table = "penalty_shootouts"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=PenaltyShootoutStatus.values),
                name="valid_penalty_shootout_status",
            ),
            models.CheckConstraint(
                condition=models.Q(winner_team_side__isnull=True)
                | models.Q(winner_team_side__in=TeamSide.values),
                name="valid_penalty_shootout_winner",
            ),
        ]


class PenaltyShootoutKick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shootout = models.ForeignKey(
        PenaltyShootout,
        on_delete=models.CASCADE,
        related_name="kicks",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="penalty_shootout_kicks",
    )
    player_name = models.CharField(max_length=NAME_MAX_LENGTH)
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    sequence_number = models.PositiveSmallIntegerField()
    outcome = models.CharField(max_length=10, choices=PenaltyKickOutcome.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(
        cls,
        *,
        shootout: PenaltyShootout,
        squad_player,
        sequence_number: int,
        outcome: PenaltyKickOutcome,
    ) -> "PenaltyShootoutKick":
        if squad_player.match_id != shootout.match_id:
            raise MatchErrors.InvalidPenaltyShootoutPlayer

        if not squad_player.is_on_field or squad_player.is_sent_off:
            raise MatchErrors.InvalidPenaltyShootoutPlayer

        team_side = TeamSide(squad_player.team_side)
        shootout.record_kick(team_side, outcome)

        return cls(
            shootout=shootout,
            player=squad_player.player,
            player_name=squad_player.player.name,
            team_side=team_side,
            sequence_number=sequence_number,
            outcome=outcome,
        )

    class Meta:
        db_table = "penalty_shootout_kicks"
        ordering = ["sequence_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["shootout", "sequence_number"],
                name="unique_penalty_shootout_kick_sequence",
            ),
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_penalty_shootout_kick_team_side",
            ),
            models.CheckConstraint(
                condition=models.Q(outcome__in=PenaltyKickOutcome.values),
                name="valid_penalty_shootout_kick_outcome",
            ),
        ]
