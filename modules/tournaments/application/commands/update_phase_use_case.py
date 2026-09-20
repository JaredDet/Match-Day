from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.domain.phase import Phase, PhaseKind
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.phase_repository import PhaseRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class UpdatePhaseUseCase:
    @inject
    def __init__(
        self, phase_repository: PhaseRepository, structure_repository: StructureRepository
    ):
        self.phase_repository = phase_repository
        self.structure_repository = structure_repository

    @transaction.atomic
    def execute(
        self,
        *,
        phase_id: UUID,
        name: str | None = None,
        kind: PhaseKind | None = None,
        order: int | None = None,
        qualifying_teams: int | None = None,
        matchdays: int | None = None,
    ) -> None:
        phase = self.structure_repository.lock_phase(phase_id)

        if phase is None:
            raise TournamentErrors.PhaseNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        if self.structure_repository.phase_has_dependencies(phase.id) and (
            (kind is not None and kind != phase.kind)
            or (matchdays is not None and matchdays < phase.matchdays)
        ):
            raise TournamentErrors.HasDependencies

        updated = Phase.create(
            season_id=phase.season_id,
            name=name if name is not None else phase.name,
            kind=kind if kind is not None else PhaseKind(phase.kind),
            order=order if order is not None else phase.order,
            qualifying_teams=qualifying_teams
            if qualifying_teams is not None
            else phase.qualifying_teams,
            matchdays=matchdays if matchdays is not None else phase.matchdays,
        )

        for field in ("name", "kind", "order", "qualifying_teams", "matchdays"):
            setattr(phase, field, getattr(updated, field))

        self.phase_repository.save(phase)
