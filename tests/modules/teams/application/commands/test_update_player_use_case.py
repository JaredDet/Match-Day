from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.teams.application.commands.update_player_use_case import UpdatePlayerUseCase
from modules.teams.domain.player import Player
from modules.teams.errors import TeamErrors

pytestmark = pytest.mark.django_db


def test_renames_and_persists_player():
    team_id = uuid4()
    player = Player.create(team_id=team_id, name="Nombre anterior")
    repository = Mock()
    repository.get_for_update.return_value = player
    repository.exists_other_by_name.return_value = False

    UpdatePlayerUseCase(repository).execute(
        team_id=team_id,
        player_id=player.id,
        name="  Nombre   nuevo  ",
    )

    assert player.name == "Nombre nuevo"
    repository.exists_other_by_name.assert_called_once_with(
        team_id=team_id,
        name="Nombre nuevo",
        player_id=player.id,
    )
    repository.save.assert_called_once_with(player)


def test_rejects_player_from_another_team():
    player = Player.create(team_id=uuid4(), name="Jugador")
    repository = Mock()
    repository.get_for_update.return_value = player

    with pytest.raises(type(TeamErrors.PlayerNotFound)) as error:
        UpdatePlayerUseCase(repository).execute(
            team_id=uuid4(),
            player_id=player.id,
            name="Nuevo nombre",
        )

    assert error.value is TeamErrors.PlayerNotFound
    repository.save.assert_not_called()


def test_rejects_name_used_by_another_player_in_team():
    team_id = uuid4()
    player = Player.create(team_id=team_id, name="Nombre anterior")
    repository = Mock()
    repository.get_for_update.return_value = player
    repository.exists_other_by_name.return_value = True

    with pytest.raises(type(TeamErrors.PlayerAlreadyExists)):
        UpdatePlayerUseCase(repository).execute(
            team_id=team_id,
            player_id=player.id,
            name="Nombre ocupado",
        )

    repository.save.assert_not_called()
