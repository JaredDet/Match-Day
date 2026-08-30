from datetime import UTC, datetime

import pytest

from modules.matches.domain.match import MatchStatus
from modules.teams.domain.team import Team
from modules.teams.infrastructure.query_repository.team_query_repository import (
    TeamQueryRepository,
)
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_lists_teams_with_last_result_and_next_match_from_their_perspective():
    atletico = Team.objects.create(name="Atlético Bahía")
    cordillera = Team.objects.create(name="Deportivo Cordillera")
    union = Team.objects.create(name="Unión del Valle")
    finished = MatchMother.create(
        home_team=atletico,
        away_team=cordillera,
        scheduled_at=datetime(2026, 8, 30, 20, tzinfo=UTC),
        status=MatchStatus.FINISHED,
    )
    finished.home_goal_count = 2
    finished.away_goal_count = 1
    finished.save()
    upcoming = MatchMother.create(
        home_team=union,
        away_team=atletico,
        scheduled_at=datetime(2026, 9, 6, 20, tzinfo=UTC),
    )
    upcoming.save()

    result = TeamQueryRepository().list()

    assert [team.name for team in result] == [
        "Atlético Bahía",
        "Deportivo Cordillera",
        "Unión del Valle",
    ]
    atletico_result, cordillera_result, union_result = result
    assert atletico_result.last_match.opponent_name == "Deportivo Cordillera"
    assert atletico_result.last_match.goals_for == 2
    assert atletico_result.last_match.goals_against == 1
    assert atletico_result.last_match.result == "win"
    assert atletico_result.next_match.opponent_name == "Unión del Valle"
    assert atletico_result.next_match.scheduled_at == upcoming.scheduled_at
    assert cordillera_result.last_match.result == "loss"
    assert cordillera_result.last_match.goals_for == 1
    assert cordillera_result.last_match.goals_against == 2
    assert cordillera_result.next_match is None
    assert union_result.last_match is None
    assert union_result.next_match.opponent_name == "Atlético Bahía"


def test_filters_teams_by_partial_case_insensitive_name():
    Team.objects.create(name="Atlético Bahía")
    Team.objects.create(name="Deportivo Cordillera")

    result = TeamQueryRepository().list(search="ATLÉTICO")

    assert [team.name for team in result] == ["Atlético Bahía"]
