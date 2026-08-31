import uuid
from unittest.mock import Mock

import pytest

from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.domain.card import CardType
from modules.matches.domain.match import MatchStatus
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_registers_card_and_updates_match_counter():
    match = MatchMother.create(status=MatchStatus.LIVE)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    player_repository = Mock()
    lineup_repository = Mock()
    lineup_repository.is_on_field.return_value = True
    player = Player.create(team_id=match.home_team_id, name="Defensor local")
    player_repository.get.return_value = player
    use_case = RegisterCardUseCase(
        match_repository,
        card_repository,
        player_repository,
        lineup_repository,
    )

    card_id = use_case.execute(
        match_id=match.id,
        player_id=player.id,
        card_type=CardType.YELLOW,
        minute=51,
    )

    card = card_repository.save.call_args.args[0]
    assert card.id == card_id
    assert card.player_name == "Defensor local"
    assert card.card_type is CardType.YELLOW
    assert match.home_card_count == 1
    assert match.away_card_count == 0
    match_repository.save.assert_called_once_with(match)


def test_raises_not_found_without_persisting():
    match_repository = Mock()
    match_repository.get_for_update.return_value = None
    card_repository = Mock()
    player_repository = Mock()
    lineup_repository = Mock()
    use_case = RegisterCardUseCase(
        match_repository,
        card_repository,
        player_repository,
        lineup_repository,
    )

    with pytest.raises(type(MatchErrors.NotFound)):
        use_case.execute(
            match_id=uuid.uuid4(),
            player_id=uuid.uuid4(),
            card_type=CardType.RED,
            minute=1,
        )

    card_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_does_not_persist_card_when_match_is_not_live():
    match = MatchMother.create()
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    player_repository = Mock()
    lineup_repository = Mock()
    player = Player.create(team_id=match.home_team_id, name="Jugador")
    player_repository.get.return_value = player
    use_case = RegisterCardUseCase(
        match_repository,
        card_repository,
        player_repository,
        lineup_repository,
    )

    with pytest.raises(type(MatchErrors.InvalidState)):
        use_case.execute(
            match_id=match.id,
            player_id=player.id,
            card_type=CardType.YELLOW,
            minute=1,
        )

    card_repository.save.assert_not_called()
    match_repository.save.assert_not_called()


def test_rejects_card_for_substitute():
    match = MatchMother.create(status=MatchStatus.LIVE)
    match_repository = Mock()
    match_repository.get_for_update.return_value = match
    card_repository = Mock()
    player_repository = Mock()
    lineup_repository = Mock()
    lineup_repository.is_on_field.return_value = False
    player = Player.create(team_id=match.home_team_id, name="Suplente")
    player_repository.get.return_value = player
    use_case = RegisterCardUseCase(
        match_repository,
        card_repository,
        player_repository,
        lineup_repository,
    )

    with pytest.raises(type(MatchErrors.PlayerNotOnField)):
        use_case.execute(
            match_id=match.id,
            player_id=player.id,
            card_type=CardType.YELLOW,
            minute=60,
        )

    card_repository.save.assert_not_called()
    match_repository.save.assert_not_called()
