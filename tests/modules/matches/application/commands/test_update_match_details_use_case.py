import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.update_match_details_use_case import (
    UpdateMatchDetailsUseCase,
)
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_updates_only_provided_details_and_persists_match():
    match = MatchMother.create()
    match.update_details(stadium_name="Estadio anterior", referee_name="Árbitro")
    repository = Mock()
    repository.get_for_update.return_value = match
    use_case = UpdateMatchDetailsUseCase(repository)

    use_case.execute(match_id=match.id, stadium_name=" Estadio nuevo ")

    assert match.stadium_name == "Estadio nuevo"
    assert match.referee_name == "Árbitro"
    repository.save.assert_called_once_with(match)


def test_raises_not_found_without_persisting():
    repository = Mock()
    repository.get_for_update.return_value = None
    use_case = UpdateMatchDetailsUseCase(repository)

    with pytest.raises(type(MatchErrors.NotFound)):
        use_case.execute(match_id=uuid.uuid4(), referee_name="Árbitro")

    repository.save.assert_not_called()
