from uuid import UUID

from modules.matches.domain.card import Card


class CardRepository:
    def get_for_update(self, match_id: UUID, card_id: UUID) -> Card | None:
        return Card.objects.select_for_update().filter(id=card_id, match_id=match_id).first()

    def save(self, card: Card) -> None:
        card.save()
