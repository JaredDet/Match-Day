from modules.matches.domain.card import Card


class CardRepository:
    def save(self, card: Card) -> None:
        card.save()
