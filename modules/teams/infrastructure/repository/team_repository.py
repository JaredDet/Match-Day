from uuid import UUID

from modules.teams.domain.team import Team


class TeamRepository:
    def get(self, team_id: UUID) -> Team | None:
        return Team.objects.filter(id=team_id).first()

    def save(self, team: Team) -> None:
        team.save()
