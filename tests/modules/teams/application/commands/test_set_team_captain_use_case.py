from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.teams.application.commands.set_team_captain_use_case import (
    SetTeamCaptainUseCase,
)
from modules.teams.errors import TeamErrors

pytestmark = pytest.mark.django_db


def test_assigns_and_saves_team_captain():
    team = Mock()
    player = Mock()
    team_repository = Mock()
    player_repository = Mock()
    team_repository.get_for_update.return_value = team
    player_repository.get.return_value = player

    SetTeamCaptainUseCase(team_repository, player_repository).execute(
        team_id=uuid4(),
        player_id=uuid4(),
    )

    team.assign_captain.assert_called_once_with(player)
    team_repository.save.assert_called_once_with(team)


def test_rejects_unknown_team_when_setting_captain():
    team_repository = Mock()
    team_repository.get_for_update.return_value = None

    with pytest.raises(type(TeamErrors.NotFound)) as error:
        SetTeamCaptainUseCase(team_repository, Mock()).execute(
            team_id=uuid4(),
            player_id=uuid4(),
        )

    assert error.value is TeamErrors.NotFound
