from modules.matches.domain.match import Match


class MatchRepository:
    def save(self, match: Match) -> None:
        match.save()
