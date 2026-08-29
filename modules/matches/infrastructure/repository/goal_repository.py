from uuid import UUID

from modules.matches.domain.goal import Goal


class GoalRepository:
    def get_for_update(self, match_id: UUID, goal_id: UUID) -> Goal | None:
        return Goal.objects.select_for_update().filter(id=goal_id, match_id=match_id).first()

    def save(self, goal: Goal) -> None:
        goal.save()
