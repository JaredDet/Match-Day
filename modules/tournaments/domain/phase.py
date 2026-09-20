from __future__ import annotations

import uuid
from uuid import UUID

from django.db import models

from modules.tournaments.domain.validation import normalize_name
from modules.tournaments.errors import TournamentErrors


class PhaseKind(models.TextChoices):
    GROUPS = "groups", "Fase de grupos"
    KNOCKOUT = "knockout", "Eliminatorias"
    THIRD_PLACE = "third_place", "Tercer puesto"


class PhaseStatus(models.TextChoices):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"


class Phase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey(
        "tournaments.Season", on_delete=models.PROTECT, related_name="phases"
    )
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=20, choices=PhaseKind.choices)
    order = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=20, choices=PhaseStatus.choices, default=PhaseStatus.SCHEDULED
    )
    qualifying_teams = models.PositiveSmallIntegerField(default=2)
    matchdays = models.PositiveSmallIntegerField(default=1)
    generated = models.BooleanField(default=False)
    source_phase = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="successors"
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expected_matches = models.PositiveSmallIntegerField(null=True, blank=True)

    @classmethod
    def create(
        cls,
        *,
        season_id: UUID,
        name: str,
        kind: PhaseKind,
        order: int,
        status: PhaseStatus = PhaseStatus.SCHEDULED,
        qualifying_teams: int = 2,
        matchdays: int = 1,
    ) -> Phase:
        if not isinstance(kind, PhaseKind):
            raise TournamentErrors.InvalidPhaseKind

        if (
            not 0 <= order <= 32767
            or not 0 <= qualifying_teams <= 32767
            or not 1 <= matchdays <= 32767
        ):
            raise TournamentErrors.InvalidPhaseConfiguration

        phase = cls(
            season_id=season_id,
            name=normalize_name(name, 100),
            kind=kind,
            order=order,
            qualifying_teams=qualifying_teams,
            matchdays=matchdays,
        )

        phase.set_status(status)

        return phase

    def set_status(self, status: PhaseStatus) -> None:
        if not isinstance(status, PhaseStatus):
            raise TournamentErrors.InvalidPhaseStatus

        self.status = status

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["season"],
                condition=models.Q(kind="third_place"),
                name="unique_season_third_place",
            ),
            models.UniqueConstraint(fields=["season", "order"], name="unique_season_phase_order"),
        ]
