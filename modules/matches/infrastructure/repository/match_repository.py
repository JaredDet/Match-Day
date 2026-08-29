from uuid import UUID

from modules.matches.domain.match import Match


class MatchRepository:
    def get_for_update(self, match_id: UUID) -> Match | None:
        return Match.objects.select_for_update().filter(id=match_id).first()

    def save(self, match: Match) -> None:
        match.save()
