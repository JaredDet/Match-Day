from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.teams.infrastructure.repository.team_repository import TeamRepository
from modules.tournaments.domain.competition_rules import CompetitionRules
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.phase import PhaseKind, PhaseStatus
from modules.tournaments.errors import TournamentErrors
from modules.tournaments.infrastructure.repository.bracket_repository import BracketRepository
from modules.tournaments.infrastructure.repository.fixture_repository import FixtureRepository
from modules.tournaments.infrastructure.repository.phase_repository import PhaseRepository
from modules.tournaments.infrastructure.repository.structure_repository import StructureRepository


class AdvanceBracketUseCase:
    @inject
    def __init__(
        self,
        structure_repository: StructureRepository,
        bracket_repository: BracketRepository,
        phase_repository: PhaseRepository,
        fixture_repository: FixtureRepository,
        match_repository: MatchRepository,
        team_repository: TeamRepository,
    ):
        self.structure_repository = structure_repository
        self.bracket_repository = bracket_repository
        self.phase_repository = phase_repository
        self.fixture_repository = fixture_repository
        self.match_repository = match_repository
        self.team_repository = team_repository

    @transaction.atomic
    def execute(self, *, season_id: UUID) -> int:
        if self.structure_repository.lock_season(season_id) is None:
            raise TournamentErrors.SeasonNotFound

        phases = [phase for phase in self.bracket_repository.phases(season_id) if phase.generated]

        if not phases:
            raise TournamentErrors.BracketNotFound

        created = 0
        by_id = {phase.id: phase for phase in phases}

        for phase in phases:
            source = by_id.get(phase.source_phase_id)

            if source is not None:
                source_fixtures = self.bracket_repository.fixtures(source.id)
                winners = [CompetitionRules.winner(f.match) for f in source_fixtures]

                if (
                    len(winners) != source.expected_matches
                    or not winners
                    or any(winner is None for winner in winners)
                ):
                    if self.bracket_repository.fixtures(phase.id):
                        raise TournamentErrors.AdvancementConflict

                    continue

                entrants = winners

                if phase.kind == PhaseKind.THIRD_PLACE:
                    entrants = [
                        f.match.away_team_id
                        if winner == f.match.home_team_id
                        else f.match.home_team_id
                        for f, winner in zip(source_fixtures, winners, strict=True)
                    ]

                pairs = list(zip(entrants[::2], entrants[1::2], strict=True))
                existing = self.bracket_repository.fixtures(phase.id)

                if existing:
                    actual = [
                        (fixture.match.home_team_id, fixture.match.away_team_id)
                        for fixture in existing
                    ]

                    if actual != pairs:
                        raise TournamentErrors.AdvancementConflict
                else:
                    for position, (home_id, away_id) in enumerate(pairs, 1):
                        match = Match.schedule(
                            home_team=self.team_repository.get(home_id),
                            away_team=self.team_repository.get(away_id),
                            scheduled_at=phase.scheduled_at,
                        )

                        self.match_repository.save(match)

                        fixture = Fixture.create(
                            phase=phase,
                            group=None,
                            match=match,
                            eligible_team_ids=set(entrants),
                            position=position,
                        )

                        self.fixture_repository.save(fixture)
                        created += 1

            fixtures = self.bracket_repository.fixtures(phase.id)

            if len(fixtures) == phase.expected_matches and all(
                CompetitionRules.winner(f.match) is not None for f in fixtures
            ):
                phase.set_status(PhaseStatus.FINISHED)

                self.phase_repository.save(phase)
            elif any(f.match.status != MatchStatus.SCHEDULED for f in fixtures):
                phase.set_status(PhaseStatus.LIVE)

                self.phase_repository.save(phase)

        return created
