import uuid
from datetime import datetime
from uuid import UUID

from django.db import models
from django.utils import timezone

from core.constants import NAME_MAX_LENGTH
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors

INITIAL_PENALTY_KICKS_PER_TEAM = 5


class PenaltyShootoutStatus(models.TextChoices):
    IN_PROGRESS = "in_progress"
    DECIDED = "decided"
    FINISHED = "finished"


class PenaltyKickOutcome(models.TextChoices):
    SCORED = "scored"
    MISSED = "missed"


class PenaltyShootoutDepartureReason(models.TextChoices):
    INJURY = "injury"
    SENT_OFF = "sent_off"


class PenaltyShootoutIneligibilityReason(models.TextChoices):
    INITIAL_EQUALIZATION = "initial_equalization"
    INJURY = "injury"
    SENT_OFF = "sent_off"
    OPPONENT_REDUCTION = "opponent_reduction"


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
    home_kick_count = models.PositiveSmallIntegerField(default=0)
    away_kick_count = models.PositiveSmallIntegerField(default=0)
    starting_team_side = models.CharField(
        max_length=10,
        choices=TeamSide.choices,
        default=TeamSide.HOME,
    )
    winner_team_side = models.CharField(
        max_length=10,
        choices=TeamSide.choices,
        null=True,
        blank=True,
    )
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def start(
        cls,
        *,
        match,
        starting_team_side: TeamSide = TeamSide.HOME,
    ) -> "PenaltyShootout":
        match.ensure_penalty_shootout_can_start()

        if not isinstance(starting_team_side, TeamSide):
            raise MatchErrors.InvalidTeamSide

        return cls(
            match=match,
            starting_team_side=starting_team_side,
        )

    def record_kick(
        self,
        *,
        team_side: TeamSide,
        player_id: UUID,
        outcome: PenaltyKickOutcome,
        eligible_player_ids: set[UUID],
        kick_counts: dict[UUID, int],
    ) -> None:
        self.ensure_kick_allowed(team_side, outcome)
        self.ensure_kicker_rotation(
            player_id=player_id,
            eligible_player_ids=eligible_player_ids,
            kick_counts=kick_counts,
        )

        if team_side == TeamSide.HOME:
            self.home_kick_count += 1
        else:
            self.away_kick_count += 1

        if outcome == PenaltyKickOutcome.SCORED:
            if team_side == TeamSide.HOME:
                self.home_score += 1
            else:
                self.away_score += 1

        self._decide_winner_if_possible()

    def ensure_kick_allowed(
        self,
        team_side: TeamSide,
        outcome: PenaltyKickOutcome,
    ) -> None:
        if self.status == PenaltyShootoutStatus.FINISHED:
            raise MatchErrors.PenaltyShootoutAlreadyFinished

        if self.status == PenaltyShootoutStatus.DECIDED:
            raise MatchErrors.PenaltyShootoutAlreadyDecided

        if not isinstance(team_side, TeamSide):
            raise MatchErrors.InvalidTeamSide

        if not isinstance(outcome, PenaltyKickOutcome):
            raise MatchErrors.InvalidPenaltyKickOutcome

        if team_side != self.next_team_side:
            raise MatchErrors.InvalidPenaltyShootoutTurn

    @staticmethod
    def ensure_kicker_rotation(
        *,
        player_id: UUID,
        eligible_player_ids: set[UUID],
        kick_counts: dict[UUID, int],
    ) -> None:
        if player_id not in eligible_player_ids:
            raise MatchErrors.InvalidPenaltyShootoutPlayer

        minimum_kick_count = min(
            (kick_counts.get(eligible_player_id, 0) for eligible_player_id in eligible_player_ids),
            default=0,
        )

        if kick_counts.get(player_id, 0) > minimum_kick_count:
            raise MatchErrors.PenaltyShootoutKickerAlreadyUsed

    def reduce_eligible_players(
        self,
        *,
        unavailable_participant: "PenaltyShootoutParticipant",
        opponent_participant: "PenaltyShootoutParticipant",
        departure_reason: PenaltyShootoutDepartureReason,
        home_eligible_count: int,
        away_eligible_count: int,
    ) -> None:
        if self.status != PenaltyShootoutStatus.IN_PROGRESS:
            raise MatchErrors.InvalidPenaltyShootoutReduction

        if not isinstance(departure_reason, PenaltyShootoutDepartureReason):
            raise MatchErrors.InvalidPenaltyShootoutDepartureReason

        participants = (unavailable_participant, opponent_participant)
        if any(participant.shootout_id != self.id for participant in participants):
            raise MatchErrors.InvalidPenaltyShootoutReduction

        if any(not participant.is_eligible for participant in participants):
            raise MatchErrors.InvalidPenaltyShootoutReduction

        if unavailable_participant.team_side == opponent_participant.team_side:
            raise MatchErrors.InvalidPenaltyShootoutReduction

        if home_eligible_count != away_eligible_count:
            raise MatchErrors.UnequalPenaltyShootoutParticipants

        unavailable_reason = PenaltyShootoutIneligibilityReason(departure_reason.value)
        unavailable_participant.make_ineligible(unavailable_reason)
        opponent_participant.make_ineligible(
            PenaltyShootoutIneligibilityReason.OPPONENT_REDUCTION,
        )

    @staticmethod
    def ensure_equal_participant_counts(
        *,
        home_eligible_count: int,
        away_eligible_count: int,
    ) -> None:
        if home_eligible_count != away_eligible_count:
            raise MatchErrors.UnequalPenaltyShootoutParticipants

    @staticmethod
    def equalize_eligible_players(
        *,
        home_player_ids: set[UUID],
        away_player_ids: set[UUID],
        excluded_player_ids: set[UUID],
    ) -> dict[TeamSide, set[UUID]]:
        if not home_player_ids or not away_player_ids:
            raise MatchErrors.InvalidPenaltyShootoutExclusions

        all_player_ids = home_player_ids | away_player_ids

        if not excluded_player_ids <= all_player_ids:
            raise MatchErrors.InvalidPenaltyShootoutExclusions

        if len(home_player_ids) == len(away_player_ids):
            expected_excluded_player_ids = set()
        elif len(home_player_ids) > len(away_player_ids):
            difference = len(home_player_ids) - len(away_player_ids)
            expected_excluded_player_ids = excluded_player_ids & home_player_ids

            if excluded_player_ids & away_player_ids:
                raise MatchErrors.InvalidPenaltyShootoutExclusions
        else:
            difference = len(away_player_ids) - len(home_player_ids)
            expected_excluded_player_ids = excluded_player_ids & away_player_ids

            if excluded_player_ids & home_player_ids:
                raise MatchErrors.InvalidPenaltyShootoutExclusions

        if len(home_player_ids) != len(away_player_ids) and (
            len(expected_excluded_player_ids) != difference
            or expected_excluded_player_ids != excluded_player_ids
        ):
            raise MatchErrors.InvalidPenaltyShootoutExclusions

        if len(home_player_ids) == len(away_player_ids) and excluded_player_ids:
            raise MatchErrors.InvalidPenaltyShootoutExclusions

        return {
            TeamSide.HOME: home_player_ids - excluded_player_ids,
            TeamSide.AWAY: away_player_ids - excluded_player_ids,
        }

    @property
    def next_team_side(self) -> TeamSide | None:
        if self.status != PenaltyShootoutStatus.IN_PROGRESS:
            return None

        starting_team_side = TeamSide(self.starting_team_side)

        if self.home_kick_count == self.away_kick_count:
            return starting_team_side

        return TeamSide.AWAY if starting_team_side == TeamSide.HOME else TeamSide.HOME

    def _decide_winner_if_possible(self) -> None:
        home_remaining = max(
            INITIAL_PENALTY_KICKS_PER_TEAM - self.home_kick_count,
            0,
        )
        away_remaining = max(
            INITIAL_PENALTY_KICKS_PER_TEAM - self.away_kick_count,
            0,
        )

        initial_phase = (
            self.home_kick_count <= INITIAL_PENALTY_KICKS_PER_TEAM
            and self.away_kick_count <= INITIAL_PENALTY_KICKS_PER_TEAM
        )
        if initial_phase:
            if self.home_score > self.away_score + away_remaining:
                self._decide(TeamSide.HOME)
                return

            if self.away_score > self.home_score + home_remaining:
                self._decide(TeamSide.AWAY)
                return

        initial_rounds_finished = (
            self.home_kick_count >= INITIAL_PENALTY_KICKS_PER_TEAM
            and self.away_kick_count >= INITIAL_PENALTY_KICKS_PER_TEAM
        )
        equal_attempts = self.home_kick_count == self.away_kick_count

        if initial_rounds_finished and equal_attempts and self.home_score != self.away_score:
            winner = TeamSide.HOME if self.home_score > self.away_score else TeamSide.AWAY
            self._decide(winner)

    def _decide(self, winner: TeamSide) -> None:
        self.status = PenaltyShootoutStatus.DECIDED
        self.winner_team_side = winner

    def finish(self, finished_at: datetime | None = None) -> None:
        if self.status == PenaltyShootoutStatus.FINISHED:
            raise MatchErrors.PenaltyShootoutAlreadyFinished

        if self.status != PenaltyShootoutStatus.DECIDED:
            raise MatchErrors.PenaltyShootoutNotDecided

        self.status = PenaltyShootoutStatus.FINISHED
        self.finished_at = finished_at or timezone.now()

    class Meta:
        db_table = "penalty_shootouts"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=PenaltyShootoutStatus.values),
                name="valid_penalty_shootout_status",
            ),
            models.CheckConstraint(
                condition=models.Q(starting_team_side__in=TeamSide.values),
                name="valid_penalty_shootout_starting_team_side",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status=PenaltyShootoutStatus.IN_PROGRESS,
                        winner_team_side__isnull=True,
                    )
                    | models.Q(
                        status__in=[
                            PenaltyShootoutStatus.DECIDED,
                            PenaltyShootoutStatus.FINISHED,
                        ],
                        winner_team_side__in=TeamSide.values,
                    )
                ),
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
        eligible_player_ids: set[UUID],
        kick_counts: dict[UUID, int],
    ) -> "PenaltyShootoutKick":
        if squad_player.match_id != shootout.match_id:
            raise MatchErrors.InvalidPenaltyShootoutPlayer

        if not squad_player.is_on_field or squad_player.is_sent_off:
            raise MatchErrors.InvalidPenaltyShootoutPlayer

        team_side = TeamSide(squad_player.team_side)
        shootout.record_kick(
            team_side=team_side,
            player_id=squad_player.player_id,
            outcome=outcome,
            eligible_player_ids=eligible_player_ids,
            kick_counts=kick_counts,
        )

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


class PenaltyShootoutParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shootout = models.ForeignKey(
        PenaltyShootout,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    player = models.ForeignKey(
        "teams.Player",
        on_delete=models.PROTECT,
        related_name="penalty_shootout_participations",
    )
    team_side = models.CharField(max_length=10, choices=TeamSide.choices)
    is_eligible = models.BooleanField(default=True)
    ineligibility_reason = models.CharField(
        max_length=25,
        choices=PenaltyShootoutIneligibilityReason.choices,
        null=True,
        blank=True,
    )
    became_ineligible_at = models.DateTimeField(null=True, blank=True)

    def make_ineligible(
        self,
        reason: PenaltyShootoutIneligibilityReason,
        occurred_at: datetime | None = None,
    ) -> None:
        if not isinstance(reason, PenaltyShootoutIneligibilityReason):
            raise MatchErrors.InvalidPenaltyShootoutDepartureReason

        if not self.is_eligible:
            raise MatchErrors.InvalidPenaltyShootoutReduction

        self.is_eligible = False
        self.ineligibility_reason = reason
        self.became_ineligible_at = occurred_at or timezone.now()

    class Meta:
        db_table = "penalty_shootout_participants"
        constraints = [
            models.UniqueConstraint(
                fields=["shootout", "player"],
                name="unique_penalty_shootout_participant",
            ),
            models.CheckConstraint(
                condition=models.Q(team_side__in=TeamSide.values),
                name="valid_penalty_shootout_participant_team_side",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        is_eligible=True,
                        ineligibility_reason__isnull=True,
                        became_ineligible_at__isnull=True,
                    )
                    | models.Q(
                        is_eligible=False,
                        ineligibility_reason__in=PenaltyShootoutIneligibilityReason.values,
                        became_ineligible_at__isnull=False,
                    )
                ),
                name="valid_penalty_shootout_participant_eligibility",
            ),
        ]
