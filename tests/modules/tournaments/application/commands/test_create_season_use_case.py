from unittest.mock import Mock
from uuid import uuid4

import pytest

from core.exceptions import AppException
from modules.teams.infrastructure.repository.team_repository import TeamRepository
from modules.tournaments.application.commands.create_season_use_case import CreateSeasonUseCase
from modules.tournaments.infrastructure.repository.season_repository import SeasonRepository
from modules.tournaments.infrastructure.repository.tournament_repository import TournamentRepository

pytestmark = pytest.mark.django_db


def test_missing_team_prevents_season_and_membership_writes():
    season_repository = Mock(spec=SeasonRepository)
    tournament_repository = Mock(spec=TournamentRepository)
    team_repository = Mock(spec=TeamRepository)
    team_repository.get.return_value = None
    use_case = CreateSeasonUseCase(season_repository, tournament_repository, team_repository)

    with pytest.raises(AppException) as error:
        use_case.execute(tournament_id=uuid4(), name="2026", team_ids=[uuid4()])

    assert error.value.code == "team_not_found"
    season_repository.save.assert_not_called()
    season_repository.set_teams.assert_not_called()


def test_missing_tournament_prevents_season_write():
    season_repository = Mock(spec=SeasonRepository)
    tournament_repository = Mock(spec=TournamentRepository)
    tournament_repository.get_for_update.return_value = None
    use_case = CreateSeasonUseCase(
        season_repository, tournament_repository, Mock(spec=TeamRepository)
    )

    with pytest.raises(AppException) as error:
        use_case.execute(tournament_id=uuid4(), name="2026")

    assert error.value.code == "tournament_not_found"
    season_repository.save.assert_not_called()
