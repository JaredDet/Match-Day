from uuid import UUID

from modules.matches.domain.card import Card


class CardRepository:
    def count_active_yellow_cards(
        self,
        *,
        match_id: UUID,
        player_id: UUID,
        exclude_card_id: UUID | None = None,
    ) -> int:
        cards = Card.objects.filter(
            match_id=match_id,
            player_id=player_id,
            card_type="yellow",
            rescinded_at__isnull=True,
        )
        if exclude_card_id is not None:
            cards = cards.exclude(id=exclude_card_id)
        return cards.count()

    def get_for_update(self, match_id: UUID, card_id: UUID) -> Card | None:
        return Card.objects.select_for_update().filter(id=card_id, match_id=match_id).first()

    def save(self, card: Card) -> None:
        card.save()
