from unittest.mock import Mock

import pytest

from modules.matches.application.commands.register_substitution_use_case import (
    RegisterSubstitutionUseCase,
)
from modules.matches.domain.match import MatchStatus
from modules.matches.errors import MatchErrors
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_rejects_player_who_already_entered_the_match():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player_out = Mock()
    player_in = Mock()
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    squad_repository = Mock()
    squad_repository.get_for_update.side_effect = [player_out, player_in]
    substitution_repository = Mock()
    substitution_repository.has_entered.return_value = True
    use_case = RegisterSubstitutionUseCase(
        match_repository,
        squad_repository,
        substitution_repository,
    )

    with pytest.raises(type(MatchErrors.InvalidSubstitutePlayer)):
        use_case.execute(
            match_id=match.id,
            player_out_id=Mock(),
            player_in_id=Mock(),
            minute=70,
        )

    squad_repository.save_all.assert_not_called()
    substitution_repository.save.assert_not_called()
