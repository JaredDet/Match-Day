import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_registers_goal_and_updates_match_score():
    match = MatchMother.create(status=MatchStatus.LIVE)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    use_case = RegisterGoalUseCase(match_repository, goal_repository)

    goal_id = use_case.execute(
        match_id=match.id,
        team_side=TeamSide.AWAY,
        player_name=" Goleador visitante ",
        minute=72,
    )

    goal = goal_repository.save.call_args.args[0]
    assert goal.id == goal_id
    assert goal.player_name == "Goleador visitante"
    assert match.away_goal_count == 1
    assert match.home_goal_count == 0
    match_repository.save.assert_called_once_with(match)


def test_raises_not_found_without_persisting():
    match_repository = Mock()
    match_repository.get_for_update.return_value = None
    goal_repository = Mock()
    use_case = RegisterGoalUseCase(match_repository, goal_repository)

    with pytest.raises(type(MatchErrors.NotFound)):
        use_case.execute(
            match_id=uuid.uuid4(),
            team_side=TeamSide.HOME,
            player_name="Jugador",
            minute=1,
        )

    goal_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_does_not_persist_goal_when_match_is_not_live():
    match = MatchMother.create()
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    use_case = RegisterGoalUseCase(match_repository, goal_repository)

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(
            match_id=match.id,
            team_side=TeamSide.HOME,
            player_name="Jugador",
            minute=1,
        )

    goal_repository.save.assert_not_called()
    match_repository.save.assert_not_called()
