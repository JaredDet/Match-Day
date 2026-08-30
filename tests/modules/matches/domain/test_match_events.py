import uuid

import pytest

from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from tests.mothers.matches.match_mother import MatchMother


def test_registers_goal_with_player_snapshot_during_live_match():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team=match.home_team, name="Goleador Local")
    event_id = uuid.uuid4()

    goal = match.register_goal(event_id=event_id, player=player, minute=34)
    player.rename("Nombre posterior")

    assert isinstance(goal, Goal)
    assert goal.id == event_id
    assert goal.player == player
    assert goal.player_name == "Goleador Local"
    assert goal.team_side == TeamSide.HOME
    assert match.home_goal_count == 1


def test_registers_card_and_derives_away_side():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team=match.away_team, name="Defensor Visitante")

    card = match.register_card(player=player, card_type=CardType.YELLOW, minute=51)

    assert isinstance(card, Card)
    assert card.player == player
    assert card.player_name == "Defensor Visitante"
    assert card.team_side == TeamSide.AWAY
    assert match.away_card_count == 1


@pytest.mark.parametrize("status", [MatchStatus.SCHEDULED, MatchStatus.FINISHED])
def test_rejects_event_when_match_is_not_live(status):
    match = MatchMother.create(status=status)
    player = Player.create(team=match.home_team, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidState)):
        match.register_goal(player=player, minute=1)


def test_rejects_player_from_team_outside_match():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team=Team.create(name="Otro equipo"), name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidPlayerTeam)) as exc_info:
        match.register_goal(player=player, minute=10)

    assert exc_info.value.code == "invalid_player_team"


@pytest.mark.parametrize("minute", [-1, 131, True])
def test_rejects_invalid_event_minute(minute):
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team=match.home_team, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidMinute)):
        match.register_goal(player=player, minute=minute)


def test_rejects_invalid_card_type():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team=match.home_team, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidCardType)):
        match.register_card(player=player, card_type="blue", minute=15)
