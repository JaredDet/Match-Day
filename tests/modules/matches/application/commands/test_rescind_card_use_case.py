import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.domain.card import CardType
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_squad_player import SentOffReason
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_rescinds_card_and_decrements_counter():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.away_team_id, name="Defensor")
    card = match.register_card(player=player, card_type=CardType.YELLOW, minute=51)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    card_repository.get_for_update.return_value = card
    card_repository.count_active_yellow_cards.return_value = 0
    use_case = RescindCardUseCase(match_repository, card_repository, Mock())

    use_case.execute(match_id=match.id, card_id=card.id)

    assert card.rescinded_at is not None
    assert match.away_card_count == 0
    card_repository.save.assert_called_once_with(card)
    match_repository.save.assert_called_once_with(match)


def test_rescinding_red_card_reinstates_player():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Defensor")
    card = match.register_card(player=player, card_type=CardType.RED, minute=70)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    card_repository.get_for_update.return_value = card
    squad_player = Mock(
        is_sent_off=True,
        sent_off_reason=SentOffReason.DIRECT_RED,
    )
    squad_repository = Mock()
    squad_repository.get_for_update.return_value = squad_player
    use_case = RescindCardUseCase(
        match_repository,
        card_repository,
        squad_repository,
    )

    use_case.execute(match_id=match.id, card_id=card.id)

    squad_player.reinstate.assert_called_once_with()
    squad_repository.save_all.assert_called_once_with([squad_player])


def test_rescinding_yellow_reverses_second_yellow_expulsion():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Defensor")
    card = match.register_card(player=player, card_type=CardType.YELLOW, minute=70)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    card_repository.get_for_update.return_value = card
    card_repository.count_active_yellow_cards.return_value = 1
    squad_player = Mock(
        is_sent_off=True,
        sent_off_reason=SentOffReason.SECOND_YELLOW,
    )
    squad_repository = Mock()
    squad_repository.get_for_update.return_value = squad_player
    use_case = RescindCardUseCase(
        match_repository,
        card_repository,
        squad_repository,
    )

    use_case.execute(match_id=match.id, card_id=card.id)

    squad_player.reinstate.assert_called_once_with()
    squad_repository.save_all.assert_called_once_with([squad_player])


def test_rejects_rescinding_card_twice():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Defensor")
    card = match.register_card(player=player, card_type=CardType.RED, minute=75)
    match.rescind_card(card)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    card_repository.get_for_update.return_value = card
    use_case = RescindCardUseCase(match_repository, card_repository, Mock())

    with pytest.raises(type(MatchErrors.CardAlreadyRescinded)):
        use_case.execute(match_id=match.id, card_id=card.id)

    assert match.home_card_count == 0
    card_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_raises_not_found_when_card_does_not_belong_to_match():
    match = MatchMother.create(status=MatchStatus.LIVE)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    card_repository.get_for_update.return_value = None
    use_case = RescindCardUseCase(match_repository, card_repository, Mock())

    with pytest.raises(type(MatchErrors.CardNotFound)):
        use_case.execute(match_id=match.id, card_id=uuid.uuid4())

    card_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_rejects_rescinding_card_when_match_is_not_live():
    match = MatchMother.create()
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    card_repository.get_for_update.return_value = Mock()
    use_case = RescindCardUseCase(match_repository, card_repository, Mock())

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(match_id=match.id, card_id=uuid.uuid4())

    card_repository.save.assert_not_called()
    match_repository.save.assert_not_called()
