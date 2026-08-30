import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.domain.match import MatchStatus
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_registers_goal_and_updates_match_score():
    match = MatchMother.create(status=MatchStatus.LIVE)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    player_repository = Mock()
    player = Player.create(team_id=match.away_team_id, name="Goleador visitante")
    player_repository.get.return_value = player
    use_case = RegisterGoalUseCase(match_repository, goal_repository, player_repository)

    goal_id = use_case.execute(
        match_id=match.id,
        player_id=player.id,
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
    player_repository = Mock()
    use_case = RegisterGoalUseCase(match_repository, goal_repository, player_repository)

    with pytest.raises(type(MatchErrors.NotFound)):
        use_case.execute(
            match_id=uuid.uuid4(),
            player_id=uuid.uuid4(),
            minute=1,
        )

    goal_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_does_not_persist_goal_when_match_is_not_live():
    match = MatchMother.create()
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    goal_repository = Mock()
    player_repository = Mock()
    player = Player.create(team_id=match.home_team_id, name="Jugador")
    player_repository.get.return_value = player
    use_case = RegisterGoalUseCase(match_repository, goal_repository, player_repository)

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(
            match_id=match.id,
            player_id=player.id,
            minute=1,
        )

    goal_repository.save.assert_not_called()
    match_repository.save.assert_not_called()
