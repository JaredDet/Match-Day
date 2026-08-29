from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.goal_repository import GoalRepository
from modules.matches.infrastructure.repository.match_repository import MatchRepository


class RegisterGoalUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        goal_repository: GoalRepository,
    ):
        self.match_repository = match_repository
        self.goal_repository = goal_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        team_side: TeamSide,
        player_name: str,
        minute: int,
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        goal = match.register_goal(
            team_side=team_side,
            player_name=player_name,
            minute=minute,
        )
        self.goal_repository.save(goal)
        self.match_repository.save(match)
        return goal.id
