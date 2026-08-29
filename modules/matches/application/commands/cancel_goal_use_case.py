from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.goal_repository import GoalRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class CancelGoalUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        goal_repository: GoalRepository,
    ):
        self.match_repository = match_repository
        self.goal_repository = goal_repository

    @transaction.atomic
    def execute(self, *, match_id: UUID, goal_id: UUID) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        goal = self.goal_repository.get_for_update(match_id, goal_id)
        if goal is None:
            raise MatchErrors.GoalNotFound
        match.cancel_goal(goal)
        self.goal_repository.save(goal)
        self.match_repository.save(match)
