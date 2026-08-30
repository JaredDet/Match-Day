import pytest

from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother


def test_adds_player_to_match_lineup():
    match = MatchMother.create()
    player = Player.create(team_id=match.home_team_id, name="CapitÃ¡n local")

    lineup_player = match.add_lineup_player(
        player=player,
        shirt_number=10,
        is_captain=True,
    )

    assert lineup_player.match == match
    assert lineup_player.player == player
    assert lineup_player.team_side == TeamSide.HOME
    assert lineup_player.shirt_number == 10
    assert lineup_player.is_captain is True


@pytest.mark.parametrize("shirt_number", [None, True, 0, 100])
def test_rejects_invalid_shirt_number(shirt_number):
    match = MatchMother.create()
    player = Player.create(team_id=match.home_team_id, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidShirtNumber)):
        match.add_lineup_player(player=player, shirt_number=shirt_number)


def test_rejects_player_from_another_team():
    match = MatchMother.create()
    other_match = MatchMother.create(
        home_team_name="Otro equipo",
        away_team_name="Otro rival",
    )
    player = Player.create(team_id=other_match.home_team_id, name="Jugador externo")

    with pytest.raises(type(MatchErrors.InvalidPlayerTeam)):
        match.add_lineup_player(player=player, shirt_number=8)
