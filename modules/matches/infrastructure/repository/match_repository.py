from uuid import UUID

from django.db import IntegrityError

from modules.matches.domain.match import Match
from modules.matches.errors import MatchErrors


class MatchRepository:
    def exists_fixture(self, fixture_key: str) -> bool:
        return Match.objects.filter(fixture_key=fixture_key).exists()

    def get_for_update(self, match_id: UUID) -> Match | None:
        return Match.objects.select_for_update().filter(id=match_id).first()

    def save(self, match: Match) -> None:
        try:
            match.save()
        except IntegrityError as error:
            if "fixture_key" in str(error):
                raise MatchErrors.AlreadyExists from error
            raise
