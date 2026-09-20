from uuid import uuid4

import pytest

from core.exceptions import AppException
from modules.matches.domain.match import Match
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.phase import Phase, PhaseKind


@pytest.mark.parametrize(
    ("kind", "group_mode", "position", "matchday", "eligible", "code"),
    [
        (PhaseKind.GROUPS, None, 1, 1, True, "invalid_tournament_fixture_group"),
        (PhaseKind.GROUPS, "other", 1, 1, True, "invalid_tournament_fixture_group"),
        (PhaseKind.KNOCKOUT, "same", 1, 1, True, "invalid_tournament_fixture_group"),
        (PhaseKind.THIRD_PLACE, None, 2, 1, True, "invalid_tournament_fixture_position"),
        (PhaseKind.KNOCKOUT, None, 1, 2, True, "invalid_tournament_matchday"),
        (PhaseKind.KNOCKOUT, None, 1, 1, False, "invalid_tournament_fixture_teams"),
    ],
)
def test_fixture_rules_do_not_require_database(
    kind, group_mode, position, matchday, eligible, code
):
    phase = Phase.create(season_id=uuid4(), name="Fase", kind=kind, order=1)
    group = Group(phase_id=phase.id if group_mode == "same" else uuid4()) if group_mode else None
    match = Match(home_team_id=uuid4(), away_team_id=uuid4())
    with pytest.raises(AppException) as error:
        Fixture.create(
            phase=phase,
            group=group,
            match=match,
            eligible_team_ids={match.home_team_id, match.away_team_id} if eligible else set(),
            position=position,
            matchday=matchday,
        )
    assert error.value.code == code
