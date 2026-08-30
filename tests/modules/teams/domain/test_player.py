import pytest

from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors


def test_creates_player_with_normalized_name():
    team = Team.create(name="Colo-Colo")

    player = Player.create(team=team, name="  Jugador   Local ")

    assert player.team == team
    assert player.name == "Jugador Local"


def test_renames_and_transfers_player():
    original_team = Team.create(name="Equipo original")
    new_team = Team.create(name="Equipo nuevo")
    player = Player.create(team=original_team, name="Jugador")

    player.rename(" Nombre nuevo ")
    player.transfer_to(new_team)

    assert player.name == "Nombre nuevo"
    assert player.team == new_team


@pytest.mark.parametrize("name", ["", "   ", None])
def test_rejects_invalid_player_name(name):
    with pytest.raises(type(TeamErrors.InvalidPlayerName)):
        Player.create(team=Team.create(name="Equipo"), name=name)
