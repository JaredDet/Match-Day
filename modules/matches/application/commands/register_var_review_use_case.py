from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.var_review import VarReviewDecision, VarReviewReason
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.var_review_repository import VarReviewRepository


class RegisterVarReviewUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        var_review_repository: VarReviewRepository,
    ):
        self.match_repository = match_repository
        self.var_review_repository = var_review_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        team_side: TeamSide,
        reason: VarReviewReason,
        decision: VarReviewDecision,
        minute: int,
        added_minute: int = 0,
        reviewed_event_id: UUID | None = None,
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        if match.status != MatchStatus.LIVE:
            raise MatchErrors.InvalidState

        if reviewed_event_id is not None and not self.var_review_repository.reviewed_event_exists(
            match_id=match.id,
            event_id=reviewed_event_id,
            reason=reason,
        ):
            raise MatchErrors.ReviewedEventNotFound

        var_review = match.register_var_review(
            team_side=team_side,
            reason=reason,
            decision=decision,
            minute=minute,
            added_minute=added_minute,
            reviewed_event_id=reviewed_event_id,
        )

        self.var_review_repository.save(var_review)

        return var_review.id
