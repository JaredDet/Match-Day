from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.utils import timezone

from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.domain.match import Match, MatchStatus
from modules.matches.errors import MatchErrors
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_creates_and_persists_scheduled_match():
    repository = Mock()
    repository.exists_fixture.return_value = False
    team_repository = Mock()
    home_team = Team.create(name="Colo-Colo")
    away_team = Team.create(name="Universidad de Chile")
    team_repository.get.side_effect = [home_team, away_team]
    use_case = CreateMatchUseCase(repository, team_repository)
    scheduled_at = timezone.now() + timedelta(days=1)

    match_id = use_case.execute(
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        scheduled_at=scheduled_at,
    )

    saved_match = repository.save.call_args.args[0]
    assert isinstance(saved_match, Match)
    assert saved_match.id == match_id
    assert saved_match.home_team == home_team
    assert saved_match.away_team == away_team
    assert saved_match.scheduled_at == scheduled_at
    assert saved_match.status == MatchStatus.SCHEDULED
    repository.save.assert_called_once_with(saved_match)


def test_rejects_duplicate_fixture_even_when_home_and_away_are_reversed():
    repository = Mock()
    repository.exists_fixture.return_value = True
    team_repository = Mock()
    home_team = Team.create(name="Colo-Colo")
    away_team = Team.create(name="Universidad de Chile")
    team_repository.get.side_effect = [away_team, home_team]
    use_case = CreateMatchUseCase(repository, team_repository)

    with pytest.raises(type(MatchErrors.AlreadyExists)) as exc_info:
        use_case.execute(
            home_team_id=away_team.id,
            away_team_id=home_team.id,
            scheduled_at=timezone.now(),
        )

    assert exc_info.value.code == "match_already_exists"
    repository.save.assert_not_called()


def test_does_not_persist_match_when_domain_rejects_teams():
    repository = Mock()
    team_repository = Mock()
    team = Team.create(name="Colo-Colo")
    team_repository.get.side_effect = [team, team]
    use_case = CreateMatchUseCase(repository, team_repository)

    with pytest.raises(type(MatchErrors.InvalidTeams)):
        use_case.execute(
            home_team_id=team.id,
            away_team_id=team.id,
            scheduled_at=timezone.now(),
        )

    repository.save.assert_not_called()
