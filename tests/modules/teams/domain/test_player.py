from uuid import uuid4

import pytest

from modules.teams.domain.player import Player, PlayerPosition
from modules.teams.errors import TeamErrors


def test_creates_player_with_normalized_name():
    team_id = uuid4()

    player = Player.create(team_id=team_id, name="  Jugador   Local ")

    assert player.team_id == team_id
    assert player.name == "Jugador Local"


def test_creates_player_with_preferred_position_and_shirt_number():
    player = Player.create(
        team_id=uuid4(),
        name="Elías Figueroa",
        preferred_position=PlayerPosition.SWEEPER,
        preferred_shirt_number=5,
    )

    assert player.preferred_position == PlayerPosition.SWEEPER
    assert player.preferred_shirt_number == 5


@pytest.mark.parametrize("shirt_number", [True, 0, 100, "10"])
def test_rejects_invalid_preferred_shirt_number(shirt_number):
    with pytest.raises(type(TeamErrors.InvalidPlayerShirtNumber)):
        Player.create(
            team_id=uuid4(),
            name="Jugador",
            preferred_shirt_number=shirt_number,
        )


def test_renames_player():
    player = Player.create(team_id=uuid4(), name="Jugador")

    player.rename(" Nombre nuevo ")

    assert player.name == "Nombre nuevo"


@pytest.mark.parametrize("name", ["", "   ", None])
def test_rejects_invalid_player_name(name):
    with pytest.raises(type(TeamErrors.InvalidPlayerName)):
        Player.create(team_id=uuid4(), name=name)
