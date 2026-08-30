from unittest.mock import Mock

import pytest

from modules.teams.application.commands.register_team_squad_use_case import (
    RegisterTeamSquadUseCase,
)
from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors

pytestmark = pytest.mark.django_db


def test_registers_complete_team_squad():
    team = Team.create(name="Colo-Colo")
    player_repository = Mock()
    player_repository.exists_by_name.return_value = False
    team_repository = Mock()
    team_repository.get_for_update.return_value = team
    use_case = RegisterTeamSquadUseCase(player_repository, team_repository)

    player_ids = use_case.execute(
        team_id=team.id,
        player_names=["Jugador uno", "Jugador dos"],
    )

    players = player_repository.save_all.call_args.args[0]
    assert tuple(player.id for player in players) == player_ids
    assert [player.name for player in players] == ["Jugador uno", "Jugador dos"]


def test_rejects_duplicate_players_inside_squad():
    team = Team.create(name="Colo-Colo")
    player_repository = Mock()
    team_repository = Mock()
    team_repository.get_for_update.return_value = team
    use_case = RegisterTeamSquadUseCase(player_repository, team_repository)

    with pytest.raises(type(TeamErrors.PlayerAlreadyExists)):
        use_case.execute(
            team_id=team.id,
            player_names=["Arturo Vidal", "  ARTURO   VIDAL "],
        )

    player_repository.save_all.assert_not_called()


def test_rejects_squad_when_player_already_belongs_to_team():
    team = Team.create(name="Colo-Colo")
    player_repository = Mock()
    player_repository.exists_by_name.side_effect = [False, True]
    team_repository = Mock()
    team_repository.get_for_update.return_value = team
    use_case = RegisterTeamSquadUseCase(player_repository, team_repository)

    with pytest.raises(type(TeamErrors.PlayerAlreadyExists)):
        use_case.execute(
            team_id=team.id,
            player_names=["Jugador nuevo", "Jugador existente"],
        )

    player_repository.save_all.assert_not_called()
