import uuid

import pytest

from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother


def test_registers_goal_during_live_match():
    match = MatchMother.create(status=MatchStatus.LIVE)
    event_id = uuid.uuid4()

    goal = match.register_goal(
        event_id=event_id,
        team_side=TeamSide.HOME,
        player_name="  Goleador Local  ",
        minute=34,
    )

    assert isinstance(goal, Goal)
    assert goal.id == event_id
    assert goal.match == match
    assert goal.team_side == TeamSide.HOME
    assert goal.player_name == "Goleador Local"
    assert goal.minute == 34
    assert match.home_goal_count == 1
    assert match.away_goal_count == 0


def test_registers_card_during_live_match():
    match = MatchMother.create(status=MatchStatus.LIVE)

    card = match.register_card(
        team_side=TeamSide.AWAY,
        player_name="Defensor Visitante",
        card_type=CardType.YELLOW,
        minute=51,
    )

    assert isinstance(card, Card)
    assert card.match == match
    assert card.card_type == CardType.YELLOW
    assert match.home_card_count == 0
    assert match.away_card_count == 1


@pytest.mark.parametrize("status", [MatchStatus.SCHEDULED, MatchStatus.FINISHED])
def test_rejects_goal_when_match_is_not_live(status):
    match = MatchMother.create(status=status)

    with pytest.raises(type(MatchErrors.InvalidState)):
        match.register_goal(
            team_side=TeamSide.HOME,
            player_name="Jugador",
            minute=1,
        )


@pytest.mark.parametrize("status", [MatchStatus.SCHEDULED, MatchStatus.FINISHED])
def test_rejects_card_when_match_is_not_live(status):
    match = MatchMother.create(status=status)

    with pytest.raises(type(MatchErrors.InvalidState)):
        match.register_card(
            team_side=TeamSide.HOME,
            player_name="Jugador",
            card_type=CardType.YELLOW,
            minute=1,
        )


@pytest.mark.parametrize(
    ("team_side", "player_name", "minute", "expected_error"),
    [
        ("neutral", "Jugador", 10, MatchErrors.InvalidTeamSide),
        (TeamSide.HOME, "  ", 10, MatchErrors.InvalidPlayerName),
        (TeamSide.HOME, "Jugador", -1, MatchErrors.InvalidMinute),
        (TeamSide.HOME, "Jugador", 131, MatchErrors.InvalidMinute),
    ],
)
def test_rejects_invalid_shared_event_data(
    team_side,
    player_name,
    minute,
    expected_error,
):
    match = MatchMother.create(status=MatchStatus.LIVE)

    with pytest.raises(type(expected_error)) as exc_info:
        match.register_goal(
            team_side=team_side,
            player_name=player_name,
            minute=minute,
        )

    assert exc_info.value.code == expected_error.code


def test_rejects_invalid_card_type():
    match = MatchMother.create(status=MatchStatus.LIVE)

    with pytest.raises(type(MatchErrors.InvalidCardType)) as exc_info:
        match.register_card(
            team_side=TeamSide.HOME,
            player_name="Jugador",
            card_type="blue",
            minute=15,
        )

    assert exc_info.value.code == "invalid_card_type"
