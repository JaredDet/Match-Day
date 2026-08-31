import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.domain.match import MatchStatus
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_disallows_goal_and_decrements_score():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Goleador")
    goal = match.register_goal(player=player, minute=54)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    goal_repository.get_for_update.return_value = goal
    use_case = DisallowGoalUseCase(match_repository, goal_repository)

    use_case.execute(match_id=match.id, goal_id=goal.id)

    assert goal.disallowed_at is not None
    assert match.home_goal_count == 0
    goal_repository.save.assert_called_once_with(goal)
    match_repository.save.assert_called_once_with(match)


def test_rejects_disallowing_goal_twice():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.away_team_id, name="Goleador")
    goal = match.register_goal(player=player, minute=60)
    match.disallow_goal(goal)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    goal_repository.get_for_update.return_value = goal
    use_case = DisallowGoalUseCase(match_repository, goal_repository)

    with pytest.raises(type(MatchErrors.GoalAlreadyDisallowed)):
        use_case.execute(match_id=match.id, goal_id=goal.id)

    assert match.away_goal_count == 0
    goal_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_raises_not_found_when_goal_does_not_belong_to_match():
    match = MatchMother.create(status=MatchStatus.LIVE)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    goal_repository.get_for_update.return_value = None
    use_case = DisallowGoalUseCase(match_repository, goal_repository)

    with pytest.raises(type(MatchErrors.GoalNotFound)):
        use_case.execute(match_id=match.id, goal_id=uuid.uuid4())

    goal_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_rejects_disallowing_goal_when_match_is_not_live():
    match = MatchMother.create()
    goal = Mock()
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    goal_repository.get_for_update.return_value = goal
    use_case = DisallowGoalUseCase(match_repository, goal_repository)

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(match_id=match.id, goal_id=uuid.uuid4())

    goal_repository.save.assert_not_called()
    match_repository.save.assert_not_called()
