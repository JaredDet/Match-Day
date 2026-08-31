from django.db import models

from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.errors import MatchErrors


class TeamSide(models.TextChoices):
    HOME = "home"
    AWAY = "away"


def validate_match_event(team_side: TeamSide, minute: int) -> None:
    if not isinstance(team_side, TeamSide):
        raise MatchErrors.InvalidTeamSide
    if (
        not isinstance(minute, int)
        or isinstance(minute, bool)
        or not MIN_MATCH_MINUTE <= minute <= MAX_MATCH_MINUTE
    ):
        raise MatchErrors.InvalidMinute
