import pytest

from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother


def test_adds_starter_to_match_squad():
    match = MatchMother.create()
    player = Player.create(team_id=match.home_team_id, name="Capitán local")

    squad_player = match.add_squad_player(
        player=player,
        shirt_number=10,
        is_captain=True,
    )

    assert squad_player.match == match
    assert squad_player.player == player
    assert squad_player.team_side == TeamSide.HOME
    assert squad_player.shirt_number == 10
    assert squad_player.role == MatchSquadRole.STARTER
    assert squad_player.is_captain is True


def test_adds_substitute_to_match_squad():
    match = MatchMother.create()
    player = Player.create(team_id=match.home_team_id, name="Suplente local")

    squad_player = match.add_squad_player(
        player=player,
        shirt_number=18,
        role=MatchSquadRole.SUBSTITUTE,
    )

    assert squad_player.role == MatchSquadRole.SUBSTITUTE


def test_rejects_substitute_captain():
    match = MatchMother.create()
    player = Player.create(team_id=match.home_team_id, name="Suplente local")

    with pytest.raises(type(MatchErrors.InvalidLineupCaptain)):
        match.add_squad_player(
            player=player,
            shirt_number=18,
            role=MatchSquadRole.SUBSTITUTE,
            is_captain=True,
        )


@pytest.mark.parametrize("shirt_number", [None, True, 0, 100])
def test_rejects_invalid_shirt_number(shirt_number):
    match = MatchMother.create()
    player = Player.create(team_id=match.home_team_id, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidShirtNumber)):
        match.add_squad_player(player=player, shirt_number=shirt_number)


def test_rejects_player_from_another_team():
    match = MatchMother.create()
    other_match = MatchMother.create(
        home_team_name="Otro equipo",
        away_team_name="Otro rival",
    )
    player = Player.create(team_id=other_match.home_team_id, name="Jugador externo")

    with pytest.raises(type(MatchErrors.InvalidPlayerTeam)):
        match.add_squad_player(player=player, shirt_number=8)
