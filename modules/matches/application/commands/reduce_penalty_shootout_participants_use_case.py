from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.penalty_shootout import PenaltyShootoutDepartureReason
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.penalty_shootout_repository import (
    PenaltyShootoutRepository,
)


class ReducePenaltyShootoutParticipantsUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        shootout_repository: PenaltyShootoutRepository,
    ):
        self.match_repository = match_repository
        self.shootout_repository = shootout_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        unavailable_player_id: UUID,
        departure_reason: PenaltyShootoutDepartureReason,
        opponent_excluded_player_id: UUID,
    ) -> None:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        shootout = self.shootout_repository.get_for_update(match.id)

        if shootout is None:
            raise MatchErrors.PenaltyShootoutNotFound

        unavailable_participant = self.shootout_repository.get_participant_for_update(
            shootout_id=shootout.id,
            player_id=unavailable_player_id,
        )
        opponent_participant = self.shootout_repository.get_participant_for_update(
            shootout_id=shootout.id,
            player_id=opponent_excluded_player_id,
        )

        if unavailable_participant is None or opponent_participant is None:
            raise MatchErrors.InvalidPenaltyShootoutReduction

        eligible_counts = self.shootout_repository.get_eligible_counts(shootout.id)
        shootout.reduce_eligible_players(
            unavailable_participant=unavailable_participant,
            opponent_participant=opponent_participant,
            departure_reason=departure_reason,
            home_eligible_count=eligible_counts[TeamSide.HOME],
            away_eligible_count=eligible_counts[TeamSide.AWAY],
        )

        self.shootout_repository.save_participant(unavailable_participant)
        self.shootout_repository.save_participant(opponent_participant)
