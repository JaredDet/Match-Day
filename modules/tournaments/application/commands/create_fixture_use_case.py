from uuid import UUID

from django.db import transaction
from injector import inject

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


class CreateFixtureUseCase:
    @inject
    def __init__(
        self,
        structure_repository: StructureRepository,
        fixture_repository: FixtureRepository,
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
        phase_id: UUID,
        match_id: UUID,
        position: int,
        group_id: UUID | None = None,
        matchday: int = 1,
    ) -> UUID:
        phase = self.structure_repository.lock_phase(phase_id)

        if phase is None:
            raise TournamentErrors.PhaseNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=False,
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        group = self.group_repository.get(group_id) if group_id else None

        if group_id and group is None:
            raise TournamentErrors.GroupNotFound

        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        eligible = (
            self.group_entry_repository.team_ids(group.id)
            if group
            else self.season_repository.team_ids(phase.season_id)
        )

        fixture = Fixture.create(
            phase=phase,
            group=group,
            match=match,
            eligible_team_ids=eligible,
            position=position,
            matchday=matchday,
        )

        self.fixture_repository.save(fixture)

        return fixture.id
