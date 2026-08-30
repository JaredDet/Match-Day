from uuid import UUID

from django.db import IntegrityError

from modules.teams.domain.team import Team
from modules.teams.errors import TeamErrors


class TeamRepository:
    def exists_by_name(self, name: str) -> bool:
        return Team.objects.filter(name__iexact=name).exists()

    def get(self, team_id: UUID) -> Team | None:
        return Team.objects.filter(id=team_id).first()

    def save(self, team: Team) -> None:
        try:
            team.save()
        except IntegrityError as error:
            if "unique_team_name_case_insensitive" in str(error):
                raise TeamErrors.AlreadyExists from error
            raise
