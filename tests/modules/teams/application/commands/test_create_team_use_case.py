from unittest.mock import Mock

import pytest

from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors

pytestmark = pytest.mark.django_db


def test_creates_and_persists_team():
    repository = Mock()
    repository.exists_by_name.return_value = False
    use_case = CreateTeamUseCase(repository)

    team_id = use_case.execute(
        name="  Universidad   de Chile  ",
        head_coach_name="  Gustavo   Alvarez  ",
        crest="teams/crests/la-u.webp",
        city="  Santiago ",
        stadium_name=" Estadio   Nacional ",
        founded_year=1927,
    )

    team = repository.save.call_args.args[0]
    assert isinstance(team, Team)
    assert team.id == team_id
    assert team.name == "Universidad de Chile"
    assert team.head_coach_name == "Gustavo Alvarez"
    assert team.crest == "teams/crests/la-u.webp"
    assert team.city == "Santiago"
    assert team.stadium_name == "Estadio Nacional"
    assert team.founded_year == 1927
    repository.exists_by_name.assert_called_once_with("Universidad de Chile")
    repository.save.assert_called_once_with(team)


def test_rejects_existing_team_name():
    repository = Mock()
    repository.exists_by_name.return_value = True
    use_case = CreateTeamUseCase(repository)

    with pytest.raises(type(TeamErrors.AlreadyExists)):
        use_case.execute(name="Colo-Colo", head_coach_name="Técnico")

    repository.save.assert_not_called()


def test_rejects_team_without_head_coach():
    repository = Mock()
    use_case = CreateTeamUseCase(repository)

    with pytest.raises(type(TeamErrors.InvalidHeadCoach)):
        use_case.execute(name="Colo-Colo")

    repository.save.assert_not_called()
