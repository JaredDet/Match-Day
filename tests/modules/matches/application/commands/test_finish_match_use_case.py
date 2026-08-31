import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_finishes_and_persists_live_match():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )
    repository = Mock()
    repository.get_for_update.return_value = match
    use_case = FinishMatchUseCase(repository)

    use_case.execute(match.id)

    repository.get_for_update.assert_called_once_with(match.id)
    repository.save.assert_called_once_with(match)
    assert match.status == MatchStatus.FINISHED
    assert match.finished_at is not None


def test_raises_not_found_without_persisting():
    match_id = uuid.uuid4()
    repository = Mock()
    repository.get_for_update.return_value = None
    use_case = FinishMatchUseCase(repository)

    with pytest.raises(type(MatchErrors.NotFound)) as exc_info:
        use_case.execute(match_id)

    assert exc_info.value.code == "match_not_found"
    repository.save.assert_not_called()


def test_does_not_persist_when_match_is_not_live():
    match = MatchMother.create()
    repository = Mock()
    repository.get_for_update.return_value = match
    use_case = FinishMatchUseCase(repository)

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(match.id)

    repository.save.assert_not_called()
