from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.card_repository import CardRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class RescindCardUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        card_repository: CardRepository,
    ):
        self.match_repository = match_repository
        self.card_repository = card_repository

    @transaction.atomic
    def execute(self, *, match_id: UUID, card_id: UUID) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        card = self.card_repository.get_for_update(match_id, card_id)
        if card is None:
            raise MatchErrors.CardNotFound
        match.rescind_card(card)
        self.card_repository.save(card)
        self.match_repository.save(match)
