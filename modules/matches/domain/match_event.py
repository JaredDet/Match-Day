from django.db import models

from modules.matches.errors import MatchErrors


class TeamSide(models.TextChoices):
    HOME = "home"
    AWAY = "away"


def validate_match_event(team_side: TeamSide, minute: int) -> None:
    if not isinstance(team_side, TeamSide):
        raise MatchErrors.InvalidTeamSide
    if not isinstance(minute, int) or isinstance(minute, bool) or not 0 <= minute <= 130:
        raise MatchErrors.InvalidMinute
