from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.card import CardType
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_squad_player import SentOffReason
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.card_repository import CardRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.player_repository import PlayerRepository


class RegisterCardUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        card_repository: CardRepository,
        player_repository: PlayerRepository,
        lineup_repository: MatchSquadRepository,
    ):
        self.match_repository = match_repository
        self.card_repository = card_repository
        self.player_repository = player_repository
        self.lineup_repository = lineup_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        player_id: UUID,
        card_type: CardType,
        minute: int,
        added_minute: int = 0,
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        if match.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState

        player = self.player_repository.get(player_id)

        if player is None:
            raise TeamErrors.PlayerNotFound

        squad_player = self.lineup_repository.get_for_update(
            match_id=match.id,
            player_id=player.id,
        )

        if squad_player is None or not squad_player.is_on_field:
            if squad_player is not None and squad_player.is_sent_off:
                raise MatchErrors.PlayerSentOff

            raise MatchErrors.PlayerNotOnField

        card = match.register_card(
            player=player,
            card_type=card_type,
            minute=minute,
            added_minute=added_minute,
        )

        sent_off_reason = None

        if card_type == CardType.RED:
            sent_off_reason = SentOffReason.DIRECT_RED

        elif (
            card_type == CardType.YELLOW
            and self.card_repository.count_active_yellow_cards(
                match_id=match.id,
                player_id=player.id,
            )
            == 1
        ):
            sent_off_reason = SentOffReason.SECOND_YELLOW

        if sent_off_reason is not None:
            squad_player.send_off(sent_off_reason)
            self.lineup_repository.save_all([squad_player])

        self.card_repository.save(card)
        self.match_repository.save(match)

        return card.id
