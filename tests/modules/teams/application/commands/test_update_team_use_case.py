from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.teams.application.commands.update_team_use_case import UpdateTeamUseCase
from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors

pytestmark = pytest.mark.django_db


def test_renames_and_persists_team():
    team = Team.create(name="Nombre anterior")
    repository = Mock()
    repository.get_for_update.return_value = team
    repository.exists_other_by_name.return_value = False
    use_case = UpdateTeamUseCase(repository)

    use_case.execute(team_id=team.id, name="  Nombre   nuevo  ")

    assert team.name == "Nombre nuevo"
    repository.exists_other_by_name.assert_called_once_with("Nombre nuevo", team.id)
    repository.save.assert_called_once_with(team)


def test_rejects_unknown_team():
    repository = Mock()
    repository.get_for_update.return_value = None
    use_case = UpdateTeamUseCase(repository)

    with pytest.raises(type(TeamErrors.NotFound)):
        use_case.execute(team_id=uuid4(), name="Nombre nuevo")

    repository.save.assert_not_called()


def test_rejects_name_used_by_another_team():
    team = Team.create(name="Nombre anterior")
    repository = Mock()
    repository.get_for_update.return_value = team
    repository.exists_other_by_name.return_value = True
    use_case = UpdateTeamUseCase(repository)

    with pytest.raises(type(TeamErrors.AlreadyExists)):
        use_case.execute(team_id=team.id, name="Nombre ocupado")

    repository.save.assert_not_called()
