from unittest.mock import Mock
from uuid import uuid4

import pytest

from core.exceptions import AppException
from modules.tournaments.application.queries.get_season_standings_query import (
    GetSeasonStandingsQuery,
)
from modules.tournaments.infrastructure.query_repository.competition_query_repository import (
    CompetitionQueryRepository,
)
from modules.tournaments.infrastructure.query_repository.season_query_repository import (
    SeasonQueryRepository,
)


def test_missing_season_is_not_reported_as_empty_standings():
    seasons = Mock(spec=SeasonQueryRepository)
    seasons.get.return_value = None
    competition = Mock(spec=CompetitionQueryRepository)

    with pytest.raises(AppException) as error:
        GetSeasonStandingsQuery(seasons, competition).execute(uuid4())

    assert error.value.code == "tournament_season_not_found"
    competition.standings.assert_not_called()
