from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import MatchStatus
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.fixture_repository import FixtureRepository
from modules.tournaments.infrastructure.repository.group_entry_repository import (
    GroupEntryRepository,
)
from modules.tournaments.infrastructure.repository.group_repository import GroupRepository
from modules.tournaments.infrastructure.repository.season_repository import SeasonRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository

_UNSET = object()


class UpdateFixtureUseCase:
    @inject
    def __init__(
        self,
        fixture_repository: FixtureRepository,
        structure_repository: StructureRepository,
        group_repository: GroupRepository,
        group_entry_repository: GroupEntryRepository,
        season_repository: SeasonRepository,
        match_repository: MatchRepository,
    ):
        self.fixture_repository = fixture_repository
        self.structure_repository = structure_repository
        self.group_repository = group_repository
        self.group_entry_repository = group_entry_repository
        self.season_repository = season_repository
        self.match_repository = match_repository

    @transaction.atomic
    def execute(
        self,
        *,
        fixture_id: UUID,
        group_id=_UNSET,
        match_id: UUID | None = None,
        position: int | None = None,
        matchday: int | None = None,
    ) -> None:
        fixture = self.fixture_repository.get(fixture_id)

        if fixture is None:
            raise TournamentErrors.FixtureNotFound

        phase = self.structure_repository.lock_phase(fixture.phase_id)
        fixture = self.fixture_repository.get_for_update(fixture_id)

        if phase is None or fixture is None:
            raise TournamentErrors.FixtureNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )
        group_id = fixture.group_id if group_id is _UNSET else group_id
        group = self.group_repository.get(group_id) if group_id else None

        if group_id and group is None:
            raise TournamentErrors.GroupNotFound

        match = self.match_repository.get_for_update(match_id or fixture.match_id)

        if match is None:
            raise MatchErrors.NotFound

        if match.status != MatchStatus.SCHEDULED:
            raise TournamentErrors.StructureLocked

        eligible = (
            self.group_entry_repository.team_ids(group.id)
            if group
            else self.season_repository.team_ids(phase.season_id)
        )
        updated = Fixture.create(
            phase=phase,
            group=group,
            match=match,
            eligible_team_ids=eligible,
            position=position if position is not None else fixture.position,
            matchday=matchday if matchday is not None else fixture.matchday,
        )

        for field in ("group_id", "match_id", "position", "matchday"):
            setattr(fixture, field, getattr(updated, field))

        self.fixture_repository.save(fixture)
