from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.matches.application.commands.register_corner_kick_use_case import (
    RegisterCornerKickUseCase,
)
from modules.matches.application.commands.register_foul_use_case import (
    RegisterFoulUseCase,
)
from modules.matches.application.commands.register_offside_use_case import (
    RegisterOffsideUseCase,
)
from modules.matches.application.commands.register_shot_use_case import (
    RegisterShotUseCase,
)
from modules.matches.application.commands.update_match_possession_use_case import (
    UpdateMatchPossessionUseCase,
)
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.shot import ShotOutcome
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from modules.teams.errors import TeamErrors
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db

STAT_EVENT_USE_CASES = (
    RegisterFoulUseCase,
    RegisterCornerKickUseCase,
    RegisterOffsideUseCase,
    RegisterShotUseCase,
)


def _build_use_case(use_case_class, *, match, player, squad_player):
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    event_repository = Mock()
    player_repository = Mock()
    player_repository.get.return_value = player
    squad_repository = Mock()
    squad_repository.get_for_update.return_value = squad_player
    use_case = use_case_class(
        match_repository,
        event_repository,
        player_repository,
        squad_repository,
    )
    return use_case, event_repository, match_repository


def _execute(use_case, *, match_id, player_id):
    kwargs = {
        "match_id": match_id,
        "player_id": player_id,
        "minute": 20,
    }
    if isinstance(use_case, RegisterShotUseCase):
        kwargs["outcome"] = ShotOutcome.OFF_TARGET

    return use_case.execute(**kwargs)


@pytest.mark.parametrize("use_case_class", STAT_EVENT_USE_CASES)
def test_stat_event_use_cases_reject_unknown_match(use_case_class):
    use_case, event_repository, match_repository = _build_use_case(
        use_case_class,
        match=None,
        player=None,
        squad_player=None,
    )

    with pytest.raises(type(MatchErrors.NotFound)):
        _execute(use_case, match_id=uuid4(), player_id=uuid4())

    event_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


@pytest.mark.parametrize("use_case_class", STAT_EVENT_USE_CASES)
def test_stat_event_use_cases_reject_match_that_is_not_live(use_case_class):
    match = MatchMother.create()
    use_case, event_repository, match_repository = _build_use_case(
        use_case_class,
        match=match,
        player=None,
        squad_player=None,
    )

    with pytest.raises(type(MatchErrors.InvalidState)):
        _execute(use_case, match_id=match.id, player_id=uuid4())

    event_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


@pytest.mark.parametrize("use_case_class", STAT_EVENT_USE_CASES)
def test_stat_event_use_cases_reject_unknown_player(use_case_class):
    match = MatchMother.create(status=MatchStatus.LIVE)
    use_case, event_repository, match_repository = _build_use_case(
        use_case_class,
        match=match,
        player=None,
        squad_player=None,
    )

    with pytest.raises(type(TeamErrors.PlayerNotFound)):
        _execute(use_case, match_id=match.id, player_id=uuid4())

    event_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


@pytest.mark.parametrize("use_case_class", STAT_EVENT_USE_CASES)
@pytest.mark.parametrize(
    ("squad_player", "expected_error"),
    [
        (None, MatchErrors.PlayerNotOnField),
        (Mock(is_on_field=False, is_sent_off=False), MatchErrors.PlayerNotOnField),
        (Mock(is_on_field=False, is_sent_off=True), MatchErrors.PlayerSentOff),
    ],
)
def test_stat_event_use_cases_reject_unavailable_player(
    use_case_class,
    squad_player,
    expected_error,
):
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Jugador")
    use_case, event_repository, match_repository = _build_use_case(
        use_case_class,
        match=match,
        player=player,
        squad_player=squad_player,
    )

    with pytest.raises(type(expected_error)):
        _execute(use_case, match_id=match.id, player_id=player.id)

    event_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_register_shot_rejects_goalkeeper_who_is_not_on_field():
    match = MatchMother.create(status=MatchStatus.LIVE)
    shooter = Player.create(team_id=match.home_team_id, name="Delantero")
    goalkeeper = Player.create(team_id=match.away_team_id, name="Arquero")
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    shot_repository = Mock()
    player_repository = Mock()
    player_repository.get.side_effect = [shooter, goalkeeper]
    squad_repository = Mock()
    squad_repository.get_for_update.side_effect = [
        Mock(is_on_field=True, is_sent_off=False),
        Mock(is_on_field=False, is_sent_off=False),
    ]
    use_case = RegisterShotUseCase(
        match_repository,
        shot_repository,
        player_repository,
        squad_repository,
    )

    with pytest.raises(type(MatchErrors.PlayerNotOnField)):
        use_case.execute(
            match_id=match.id,
            player_id=shooter.id,
            goalkeeper_id=goalkeeper.id,
            outcome=ShotOutcome.SAVED,
            minute=20,
        )

    shot_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_update_possession_rejects_unknown_match():
    match_repository = Mock()
    match_repository.get_for_update.return_value = None
    use_case = UpdateMatchPossessionUseCase(match_repository)

    with pytest.raises(type(MatchErrors.NotFound)):
        use_case.execute(match_id=uuid4(), home_percentage=50)

    match_repository.save.assert_not_called()


def test_update_possession_rejects_match_that_is_not_live():
    match = MatchMother.create()
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    use_case = UpdateMatchPossessionUseCase(match_repository)

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(match_id=match.id, home_percentage=50)

    match_repository.save.assert_not_called()
