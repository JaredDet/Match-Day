from uuid import uuid4

import pytest

from modules.teams.domain.player import Player
from modules.teams.errors import TeamErrors


def test_creates_player_with_normalized_name():
    team_id = uuid4()

    player = Player.create(team_id=team_id, name="  Jugador   Local ")

    assert player.team_id == team_id
    assert player.name == "Jugador Local"


def test_renames_player():
    player = Player.create(team_id=uuid4(), name="Jugador")

    player.rename(" Nombre nuevo ")

    assert player.name == "Nombre nuevo"


@pytest.mark.parametrize("name", ["", "   ", None])
def test_rejects_invalid_player_name(name):
    with pytest.raises(type(TeamErrors.InvalidPlayerName)):
        Player.create(team_id=uuid4(), name=name)
