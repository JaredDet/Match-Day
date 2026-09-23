from uuid import UUID

from django.db import transaction
from injector import inject

from modules.teams.errors import TeamErrors
from modules.teams.infrastructure.repository.team_repository import TeamRepository

_UNSET = object()


class UpdateTeamUseCase:
    @inject
    def __init__(self, team_repository: TeamRepository):
        self.team_repository = team_repository

    @transaction.atomic
    def execute(
        self,
        *,
        team_id: UUID,
        name: str | None = None,
        head_coach_name: str | object = _UNSET,
        crest: object = _UNSET,
        city: str | None | object = _UNSET,
        stadium_name: str | None | object = _UNSET,
        founded_year: int | None | object = _UNSET,
    ) -> None:
        team = self.team_repository.get_for_update(team_id)
        if team is None:
            raise TeamErrors.NotFound

        if name is not None:
            team.rename(name)

        if name is not None and self.team_repository.exists_other_by_name(team.name, team.id):
            raise TeamErrors.AlreadyExists

        if head_coach_name is not _UNSET:
            if not isinstance(head_coach_name, str) or not head_coach_name.strip():
                raise TeamErrors.InvalidHeadCoach
            team.set_head_coach(head_coach_name)

        if any(value is not _UNSET for value in (crest, city, stadium_name, founded_year)):
            team.update_profile(
                crest=team.crest if crest is _UNSET else crest,
                city=team.city if city is _UNSET else city,
                stadium_name=team.stadium_name if stadium_name is _UNSET else stadium_name,
                founded_year=team.founded_year if founded_year is _UNSET else founded_year,
            )

        self.team_repository.save(team)
