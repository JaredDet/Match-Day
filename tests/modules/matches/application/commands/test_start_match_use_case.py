import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def _ready_squad():
    return [
        Mock(
            team_side=team_side,
            role=MatchSquadRole.STARTER,
            is_on_field=True,
            is_captain=index == 0,
        )
        for team_side in TeamSide
        for index in range(11)
    ]


def test_starts_and_persists_scheduled_match():
    match = MatchMother.create()
    match.home_formation = MatchFormation.FOUR_THREE_THREE
    match.away_formation = MatchFormation.FOUR_FOUR_TWO
    repository = Mock()
    repository.get_for_update.return_value = match
    squad_repository = Mock()
    squad_repository.list_for_update.return_value = _ready_squad()
    use_case = StartMatchUseCase(repository, squad_repository)

    use_case.execute(match.id)

    repository.get_for_update.assert_called_once_with(match.id)
    squad_repository.list_for_update.assert_called_once_with(match_id=match.id)
    repository.save.assert_called_once_with(match)
    assert match.status == MatchStatus.LIVE
    assert match.started_at is not None


def test_raises_not_found_without_persisting():
    match_id = uuid.uuid4()
    repository = Mock()
    repository.get_for_update.return_value = None
    use_case = StartMatchUseCase(repository, Mock())

    with pytest.raises(type(MatchErrors.NotFound)) as exc_info:
        use_case.execute(match_id)

    assert exc_info.value.code == "match_not_found"
    repository.save.assert_not_called()


def test_does_not_persist_when_match_is_already_live():
    match = MatchMother.create(status=MatchStatus.LIVE)
    repository = Mock()
    repository.get_for_update.return_value = match
    use_case = StartMatchUseCase(repository, Mock())

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(match.id)

    repository.save.assert_not_called()


def test_rejects_start_without_both_formations():
    match = MatchMother.create()
    repository = Mock()
    repository.get_for_update.return_value = match
    squad_repository = Mock()
    squad_repository.list_for_update.return_value = _ready_squad()
    use_case = StartMatchUseCase(repository, squad_repository)

    with pytest.raises(type(MatchErrors.MissingFormation)):
        use_case.execute(match.id)

    repository.save.assert_not_called()


def test_rejects_start_without_eleven_starters_per_team():
    match = MatchMother.create()
    match.home_formation = MatchFormation.FOUR_THREE_THREE
    match.away_formation = MatchFormation.FOUR_FOUR_TWO
    repository = Mock()
    repository.get_for_update.return_value = match
    squad_repository = Mock()
    squad_repository.list_for_update.return_value = _ready_squad()[:-1]
    use_case = StartMatchUseCase(repository, squad_repository)

    with pytest.raises(type(MatchErrors.InvalidStartingSquad)):
        use_case.execute(match.id)

    repository.save.assert_not_called()
