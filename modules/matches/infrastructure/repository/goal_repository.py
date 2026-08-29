from modules.matches.domain.goal import Goal


class GoalRepository:
    def save(self, goal: Goal) -> None:
        goal.save()
