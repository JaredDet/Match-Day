from datetime import timedelta

from django.utils import timezone

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.teams.domain.team import Team


class MatchMother:
    @staticmethod
    def create(
        *,
        home_team_name: str = "Colo-Colo",
        away_team_name: str = "Universidad de Chile",
        home_team: Team | None = None,
        away_team: Team | None = None,
        persist_teams: bool = False,
        scheduled_at=None,
        status: str = MatchStatus.SCHEDULED,
        current_period: MatchPeriod | None = None,
        current_minute: int | None = None,
    ) -> Match:
        home_team = home_team or Team.create(name=home_team_name)
        away_team = away_team or Team.create(name=away_team_name)
        if persist_teams:
            home_team.save()
            away_team.save()
        match = Match.schedule(
            home_team=home_team,
            away_team=away_team,
            scheduled_at=scheduled_at or timezone.now() + timedelta(hours=1),
        )
        match.status = status
        if status in {MatchStatus.LIVE, MatchStatus.FINISHED}:
            match.started_at = timezone.now()
            match.current_period = current_period or MatchPeriod.SECOND_HALF
            if match.current_period == MatchPeriod.FIRST_HALF:
                match.current_minute = current_minute or 45
            elif match.current_period == MatchPeriod.HALFTIME:
                match.current_minute = 45
            else:
                match.current_minute = current_minute or 90
        if status == MatchStatus.FINISHED:
            match.current_period = MatchPeriod.SECOND_HALF
            match.current_minute = 90
            match.finished_at = match.started_at + timedelta(hours=2)
        return match
