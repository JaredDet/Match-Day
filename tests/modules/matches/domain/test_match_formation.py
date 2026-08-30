import pytest

from modules.matches.domain.match import MatchFormation
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother


@pytest.mark.parametrize(
    ("team_side", "formation", "field"),
    [
        (TeamSide.HOME, MatchFormation.FOUR_TWO_THREE_ONE, "home_formation"),
        (TeamSide.AWAY, MatchFormation.THREE_FOUR_THREE, "away_formation"),
    ],
)
def test_sets_team_formation(team_side, formation, field):
    match = MatchMother.create()

    match.set_formation(team_side=team_side, formation=formation)

    assert getattr(match, field) == formation


def test_rejects_invalid_formation():
    with pytest.raises(type(MatchErrors.InvalidFormation)):
        MatchMother.create().set_formation(
            team_side=TeamSide.HOME,
            formation="4-4-3",
        )


def test_rejects_invalid_team_side():
    with pytest.raises(type(MatchErrors.InvalidTeamSide)):
        MatchMother.create().set_formation(
            team_side="neutral",
            formation=MatchFormation.FOUR_THREE_THREE,
        )
