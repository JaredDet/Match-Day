import pytest

from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors


def test_creates_team_with_normalized_name():
    team = Team.create(name="  Universidad   de   Chile  ")

    assert team.name == "Universidad de Chile"


def test_renames_team_with_normalized_name():
    team = Team.create(name="Nombre anterior")

    team.rename("  Nombre   nuevo ")

    assert team.name == "Nombre nuevo"


def test_assigns_player_from_team_as_captain():
    team = Team.create(name="Colo-Colo")
    player = Player.create(team_id=team.id, name="Arturo Vidal")

    team.assign_captain(player)

    assert team.captain == player


def test_rejects_captain_from_another_team():
    team = Team.create(name="Colo-Colo")
    player = Player.create(team_id=Team.create(name="Otro equipo").id, name="Jugador")

    with pytest.raises(type(TeamErrors.InvalidCaptain)) as error:
        team.assign_captain(player)

    assert error.value is TeamErrors.InvalidCaptain


@pytest.mark.parametrize("name", ["", "   ", None])
def test_rejects_invalid_team_name(name):
    with pytest.raises(type(TeamErrors.InvalidName)) as exc_info:
        Team.create(name=name)

    assert exc_info.value.code == "invalid_team_name"
