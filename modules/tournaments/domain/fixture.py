from __future__ import annotations

import uuid
from uuid import UUID

from django.db import models

from modules.matches.domain.match import Match
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.phase import Phase, PhaseKind
from modules.tournaments.errors import TournamentErrors


class Fixture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.ForeignKey(
        "tournaments.Phase", on_delete=models.PROTECT, related_name="fixtures"
    )
    group = models.ForeignKey(
        "tournaments.Group",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="fixtures",
    )
    match = models.OneToOneField(
        "matches.Match", on_delete=models.PROTECT, related_name="tournament_fixture"
    )
    position = models.PositiveSmallIntegerField()
    matchday = models.PositiveSmallIntegerField(default=1)

    @classmethod
    def create(
        cls,
        *,
        phase: Phase,
        group: Group | None,
        match: Match,
        eligible_team_ids: set[UUID],
        position: int,
        matchday: int = 1,
    ) -> Fixture:
        if not 0 <= position <= 32767 or (phase.kind == PhaseKind.THIRD_PLACE and position != 1):
            raise TournamentErrors.InvalidFixturePosition

        if phase.kind == PhaseKind.GROUPS:
            if group is None or group.phase_id != phase.id:
                raise TournamentErrors.InvalidFixtureGroup
        elif group is not None:
            raise TournamentErrors.InvalidFixtureGroup

        if not {match.home_team_id, match.away_team_id}.issubset(eligible_team_ids):
            raise TournamentErrors.InvalidFixtureTeams

        if not 1 <= matchday <= phase.matchdays:
            raise TournamentErrors.InvalidMatchday

        return cls(
            phase_id=phase.id,
            group_id=group.id if group else None,
            match_id=match.id,
            position=position,
            matchday=matchday,
        )

    class Meta:
        ordering = ["phase__order", "position", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["phase", "position"], name="unique_phase_fixture_position"
            )
        ]
