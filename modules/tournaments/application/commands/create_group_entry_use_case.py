from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.group_entry_repository import (
    GroupEntryRepository,
)
from modules.tournaments.infrastructure.repository.group_repository import GroupRepository
from modules.tournaments.infrastructure.repository.season_repository import SeasonRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository
from modules.tournaments.infrastructure.repository.tournament_repository import TournamentRepository


class CreateGroupEntryUseCase:
    @inject
    def __init__(
        self,
        structure_repository: StructureRepository,
        group_entry_repository: GroupEntryRepository,
        group_repository: GroupRepository,
        season_repository: SeasonRepository,
        tournament_repository: TournamentRepository,
    ):
        self.group_entry_repository = group_entry_repository
        self.group_repository = group_repository
        self.structure_repository = structure_repository
        self.season_repository = season_repository
        self.tournament_repository = tournament_repository

    @transaction.atomic
    def execute(self, *, group_id: UUID, team_id: UUID) -> UUID:
        group = self.group_repository.get(group_id)

        if group is None:
            raise TournamentErrors.GroupNotFound

        phase = self.structure_repository.lock_phase(group.phase_id)
        group = self.group_repository.get_for_update(group_id)

        if phase is None or group is None:
            raise TournamentErrors.GroupNotFound

        CompetitionRules.ensure_mutable(
            phase,
            has_started=self.structure_repository.has_started(phase.id),
            has_successors=self.structure_repository.has_successors(phase.id),
        )

        entry = GroupEntry.create(
            group=group,
            team_id=team_id,
            registered_team_ids=self.season_repository.team_ids(phase.season_id),
        )

        season = self.season_repository.get(phase.season_id)
        tournament = self.tournament_repository.get(season.tournament_id)

        if self.group_entry_repository.exists_in_phase(phase.id, team_id):
            raise TournamentErrors.GroupEntryAlreadyExists

        tournament.ensure_group_capacity(self.group_entry_repository.count_by_group(group.id))

        self.group_entry_repository.save(entry)
        self.structure_repository.clear_tie_break(group.id)

        return entry.id
