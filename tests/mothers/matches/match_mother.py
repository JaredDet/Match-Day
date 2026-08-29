from datetime import timedelta

from django.utils import timezone

from modules.matches.domain.match import Match, MatchStatus


class MatchMother:
    @staticmethod
    def create(
        *,
        home_team_name: str = "Colo-Colo",
        away_team_name: str = "Universidad de Chile",
        scheduled_at=None,
        status: str = MatchStatus.SCHEDULED,
    ) -> Match:
        match = Match.schedule(
            home_team_name=home_team_name,
            away_team_name=away_team_name,
            scheduled_at=scheduled_at or timezone.now() + timedelta(hours=1),
        )
        match.status = status
        if status in {MatchStatus.LIVE, MatchStatus.FINISHED}:
            match.started_at = timezone.now()
        if status == MatchStatus.FINISHED:
            match.finished_at = match.started_at + timedelta(hours=2)
        return match
