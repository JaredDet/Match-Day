from uuid import UUID

from django.db.models import Q

from modules.matches.domain.match import Match, MatchStatus
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.domain.phase import Phase
from modules.tournaments.domain.season import Season


class StructureRepository:
    def lock_season(self, season_id: UUID):
        return Season.objects.select_for_update().filter(id=season_id).first()

    def lock_phase(self, phase_id: UUID):
        phase = Phase.objects.filter(id=phase_id).first()

        if phase is None:
            return None

        self.lock_season(phase.season_id)

        return Phase.objects.select_for_update().filter(id=phase_id).first()

    def has_started(self, phase_id):
        matches = Match.objects.select_for_update().filter(tournament_fixture__phase_id=phase_id)

        return any(match.status != MatchStatus.SCHEDULED for match in list(matches))

    def has_successors(self, phase_id):
        return Phase.objects.filter(source_phase_id=phase_id).exists()

    def phase_has_dependencies(self, phase_id):
        return (
            Group.objects.filter(phase_id=phase_id).exists()
            or Fixture.objects.filter(phase_id=phase_id).exists()
        )

    def group_has_dependencies(self, group_id):
        return (
            GroupEntry.objects.filter(group_id=group_id).exists()
            or Fixture.objects.filter(group_id=group_id).exists()
        )

    def team_is_used(self, season_id, team_id):
        return (
            GroupEntry.objects.filter(phase__season_id=season_id, team_id=team_id).exists()
            or Fixture.objects.filter(phase__season_id=season_id)
            .filter(Q(match__home_team_id=team_id) | Q(match__away_team_id=team_id))
            .exists()
        )

    def entry_has_fixtures(self, entry):
        return (
            Fixture.objects.filter(group_id=entry.group_id)
            .filter(Q(match__home_team_id=entry.team_id) | Q(match__away_team_id=entry.team_id))
            .exists()
        )

    def season_has_generated_phases(self, season_id):
        return Phase.objects.filter(season_id=season_id, generated=True).exists()

    def add_team(self, season, team_id):
        season.teams.add(team_id)

    def remove_team(self, season, team_id):
        season.teams.remove(team_id)

    def delete(self, entity):
        entity.delete()

    def clear_tie_break(self, group_id):
        Group.objects.filter(id=group_id).update(tie_break_order=[])
