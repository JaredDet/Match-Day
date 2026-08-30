import pytest

from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors


def test_creates_team_with_normalized_name():
    team = Team.create(name="  Universidad   de   Chile  ")

    assert team.name == "Universidad de Chile"


def test_renames_team_with_normalized_name():
    team = Team.create(name="Nombre anterior")

    team.rename("  Nombre   nuevo ")

    assert team.name == "Nombre nuevo"


@pytest.mark.parametrize("name", ["", "   ", None])
def test_rejects_invalid_team_name(name):
    with pytest.raises(type(TeamErrors.InvalidName)) as exc_info:
        Team.create(name=name)

    assert exc_info.value.code == "invalid_team_name"
