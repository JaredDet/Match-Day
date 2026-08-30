from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.teams.application.commands.register_player_use_case import RegisterPlayerUseCase
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors

pytestmark = pytest.mark.django_db


def test_registers_player_for_team():
    team = Team.create(name="Colo-Colo")
    player_repository = Mock()
    player_repository.exists_by_name.return_value = False
    team_repository = Mock()
    team_repository.get_for_update.return_value = team
    use_case = RegisterPlayerUseCase(player_repository, team_repository)

    player_id = use_case.execute(team_id=team.id, name="  Arturo   Vidal ")

    player = player_repository.save.call_args.args[0]
    assert isinstance(player, Player)
    assert player.id == player_id
    assert player.team == team
    assert player.name == "Arturo Vidal"


def test_rejects_player_for_unknown_team():
    player_repository = Mock()
    team_repository = Mock()
    team_repository.get_for_update.return_value = None
    use_case = RegisterPlayerUseCase(player_repository, team_repository)

    with pytest.raises(type(TeamErrors.NotFound)):
        use_case.execute(team_id=uuid4(), name="Jugador")

    player_repository.save.assert_not_called()


def test_rejects_existing_player_in_team():
    team = Team.create(name="Colo-Colo")
    player_repository = Mock()
    player_repository.exists_by_name.return_value = True
    team_repository = Mock()
    team_repository.get_for_update.return_value = team
    use_case = RegisterPlayerUseCase(player_repository, team_repository)

    with pytest.raises(type(TeamErrors.PlayerAlreadyExists)):
        use_case.execute(team_id=team.id, name="Arturo Vidal")

    player_repository.save.assert_not_called()
