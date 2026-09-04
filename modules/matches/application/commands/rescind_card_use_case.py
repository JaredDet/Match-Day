from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.card import CardType
from modules.matches.domain.match_squad_player import SentOffReason
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.card_repository import CardRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)


class RescindCardUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        card_repository: CardRepository,
        squad_repository: MatchSquadRepository,
    ):
        self.match_repository = match_repository
        self.card_repository = card_repository
        self.squad_repository = squad_repository

    @transaction.atomic
    def execute(self, *, match_id: UUID, card_id: UUID) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound

        card = self.card_repository.get_for_update(match_id, card_id)
        if card is None:
            raise MatchErrors.CardNotFound

        match.rescind_card(card)

        should_reinstate = card.card_type == CardType.RED
        if card.card_type == CardType.YELLOW:
            remaining_yellows = self.card_repository.count_active_yellow_cards(
                match_id=match.id,
                player_id=card.player_id,
                exclude_card_id=card.id,
            )
            should_reinstate = remaining_yellows < 2

        if should_reinstate:
            squad_player = self.squad_repository.get_for_update(
                match_id=match.id,
                player_id=card.player_id,
            )
            expected_reason = (
                SentOffReason.DIRECT_RED
                if card.card_type == CardType.RED
                else SentOffReason.SECOND_YELLOW
            )
            if (
                squad_player is not None
                and squad_player.is_sent_off
                and squad_player.sent_off_reason == expected_reason
            ):
                squad_player.reinstate()
                self.squad_repository.save_all([squad_player])

        self.card_repository.save(card)
        self.match_repository.save(match)
