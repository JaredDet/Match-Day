from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository

_UNSET = object()


class UpdateMatchDetailsUseCase:
    @inject
    def __init__(self, match_repository: MatchRepository):
        self.match_repository = match_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        stadium_name=_UNSET,
        referee_name=_UNSET,
    ) -> None:
        match = self.match_repository.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound

        details = {}
        if stadium_name is not _UNSET:
            details["stadium_name"] = stadium_name
        if referee_name is not _UNSET:
            details["referee_name"] = referee_name
        match.update_details(**details)
        self.match_repository.save(match)
