from uuid import UUID

from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal, GoalType
from modules.matches.domain.penalty_attempt import PenaltyAttempt
from modules.matches.domain.var_review import VarReview, VarReviewReason


class VarReviewRepository:
    def reviewed_event_exists(
        self,
        *,
        match_id: UUID,
        event_id: UUID,
        reason: VarReviewReason,
    ) -> bool:
        if reason == VarReviewReason.GOAL:
            return Goal.objects.filter(match_id=match_id, id=event_id).exists()

        if reason == VarReviewReason.PENALTY:
            return (
                Goal.objects.filter(
                    match_id=match_id,
                    id=event_id,
                    goal_type=GoalType.PENALTY,
                ).exists()
                or PenaltyAttempt.objects.filter(match_id=match_id, id=event_id).exists()
            )

        cards = Card.objects.filter(match_id=match_id, id=event_id)

        if reason == VarReviewReason.DIRECT_RED_CARD:
            cards = cards.filter(card_type=CardType.RED)

        return cards.exists()

    def save(self, var_review: VarReview) -> None:
        var_review.save()
