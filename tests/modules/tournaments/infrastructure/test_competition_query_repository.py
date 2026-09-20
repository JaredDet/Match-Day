from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from modules.matches.domain.match import Match
from modules.matches.domain.penalty_shootout import PenaltyShootout
from modules.teams.domain.team import Team
from modules.tournaments.api.contracts.responses.get_season_bracket_response import (
    GetSeasonBracketResponse,
)
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.phase import Phase, PhaseKind
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament
from modules.tournaments.infrastructure.query_repository.competition_query_repository import (
    CompetitionQueryRepository,
)

pytestmark = pytest.mark.django_db


def test_bracket_is_detached_from_orm_and_serializes_penalties(django_assert_num_queries):
    tournament = Tournament.objects.create(
        slug="copa", name="Copa", country="Chile", category="Copa"
    )
    season = Season.objects.create(tournament=tournament, name="2026")
    phase = Phase.objects.create(season=season, name="Final", kind=PhaseKind.KNOCKOUT, order=1)
    home, away = Team.objects.create(name="Local"), Team.objects.create(name="Visita")
    match = Match.schedule(
        home_team=home, away_team=away, scheduled_at=datetime(2026, 9, 1, tzinfo=UTC)
    )
    match.start(datetime(2026, 9, 1, tzinfo=UTC))
    match.save()
    PenaltyShootout.objects.create(match=match, home_score=3, away_score=2)
    Fixture.objects.create(phase=phase, match=match, position=1)

    result = CompetitionQueryRepository().bracket(season.id)

    with django_assert_num_queries(0):
        response = GetSeasonBracketResponse(result).data
    assert response["rounds"][0]["ties"][0]["penalties"] == [3, 2]
    assert response["rounds"][0]["ties"][0]["homeScore"] == 0
    with pytest.raises(FrozenInstanceError):
        result.third = None
