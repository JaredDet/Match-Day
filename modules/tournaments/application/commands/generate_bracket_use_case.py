from datetime import datetime, timedelta
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from injector import inject

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository
from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.phase import Phase, PhaseKind, PhaseStatus
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.query_repository.competition_query_repository import (
    CompetitionQueryRepository,
)
from modules.tournaments.infrastructure.repository.bracket_repository import BracketRepository
from modules.tournaments.infrastructure.repository.fixture_repository import FixtureRepository
from modules.tournaments.infrastructure.repository.phase_repository import PhaseRepository
from modules.tournaments.infrastructure.repository.season_repository import SeasonRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository

ROUND_NAMES = {
    64: "32vos de final",
    32: "16vos de final",
    16: "Octavos de final",
    8: "Cuartos de final",
    4: "Semifinales",
    2: "Final",
}


class GenerateBracketUseCase:
    @inject
    def __init__(
        self,
        structure_repository: StructureRepository,
        bracket_repository: BracketRepository,
        season_repository: SeasonRepository,
        phase_repository: PhaseRepository,
        fixture_repository: FixtureRepository,
        match_repository: MatchRepository,
        team_repository: TeamRepository,
        competition_query_repository: CompetitionQueryRepository,
    ):
        self.structure_repository = structure_repository
        self.bracket_repository = bracket_repository
        self.season_repository = season_repository
        self.phase_repository = phase_repository
        self.fixture_repository = fixture_repository
        self.match_repository = match_repository
        self.team_repository = team_repository
        self.competition_query_repository = competition_query_repository

    @transaction.atomic
    def execute(
        self,
        *,
        season_id: UUID,
        starts_at: datetime,
        team_ids: list[UUID] | None = None,
        source_phase_id: UUID | None = None,
        round_interval_days: int = 7,
        third_place: bool = True,
    ) -> tuple[UUID, ...]:
        season = self.structure_repository.lock_season(season_id)

        if season is None:
            raise TournamentErrors.SeasonNotFound

        if self.bracket_repository.has_knockout(season_id):
            raise TournamentErrors.BracketAlreadyExists

        if (
            timezone.is_naive(starts_at)
            or not 1 <= round_interval_days <= 365
            or (team_ids is None) == (source_phase_id is None)
        ):
            raise TournamentErrors.InvalidBracket

        if source_phase_id is not None:
            source = self.phase_repository.get(source_phase_id)

            if source is None or source.season_id != season_id or source.kind != PhaseKind.GROUPS:
                raise TournamentErrors.InvalidBracket

            fixtures = self.bracket_repository.fixtures(source.id)

            if (
                source.status != PhaseStatus.FINISHED
                or not fixtures
                or any(f.match.status != MatchStatus.FINISHED for f in fixtures)
            ):
                raise TournamentErrors.IncompletePhase

            groups = [
                group
                for group in self.competition_query_repository.standings(season_id)
                if group.phase_id == source.id
            ]

            if (
                not groups
                or source.qualifying_teams < 1
                or any(
                    len(group.rows) < source.qualifying_teams
                    or any(row.played == 0 for row in group.rows)
                    for group in groups
                )
            ):
                raise TournamentErrors.IncompletePhase

            selected = [
                group.rows[rank] for rank in range(source.qualifying_teams) for group in groups
            ]

            if any(row.tie_break_required for row in selected):
                raise TournamentErrors.UnresolvedTie

            team_ids = [row.id for row in selected]

        CompetitionRules.validate_entrants(team_ids, self.season_repository.team_ids(season_id))
        existing = self.bracket_repository.phases(season_id)
        order = max((phase.order for phase in existing), default=-1) + 1
        entrants = len(team_ids)
        rounds = []
        previous = source_phase_id
        semifinal = None

        while entrants >= 2:
            phase = Phase.create(
                season_id=season_id,
                name=ROUND_NAMES[entrants],
                kind=PhaseKind.KNOCKOUT,
                order=order,
            )
            phase.generated = True
            phase.source_phase_id = previous
            phase.expected_matches = entrants // 2
            phase.scheduled_at = starts_at + timedelta(days=round_interval_days * len(rounds))

            self.phase_repository.save(phase)
            rounds.append(phase)

            if entrants == 4:
                semifinal = phase

            previous = phase.id
            entrants //= 2
            order += 1

        first = rounds[0]

        for position in range(len(team_ids) // 2):
            match = Match.schedule(
                home_team=self.team_repository.get(team_ids[position]),
                away_team=self.team_repository.get(team_ids[-position - 1]),
                scheduled_at=first.scheduled_at,
            )

            self.match_repository.save(match)

            fixture = Fixture.create(
                phase=first,
                group=None,
                match=match,
                eligible_team_ids=set(team_ids),
                position=position + 1,
            )

            self.fixture_repository.save(fixture)

        if third_place and semifinal is not None:
            phase = Phase.create(
                season_id=season_id, name="Tercer puesto", kind=PhaseKind.THIRD_PLACE, order=order
            )
            phase.generated = True
            phase.source_phase_id = semifinal.id
            phase.expected_matches = 1
            phase.scheduled_at = rounds[-1].scheduled_at

            self.phase_repository.save(phase)
            rounds.append(phase)

        return tuple(phase.id for phase in rounds)
