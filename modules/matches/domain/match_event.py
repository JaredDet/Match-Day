from django.db import models

from modules.matches.errors import MatchErrors


class TeamSide(models.TextChoices):
    HOME = "home"
    AWAY = "away"


def validate_match_event(team_side: TeamSide, player_name: str, minute: int) -> str:
    if not isinstance(team_side, TeamSide):
        raise MatchErrors.InvalidTeamSide
    normalized_player_name = player_name.strip() if player_name else ""
    if not normalized_player_name:
        raise MatchErrors.InvalidPlayerName
    if not isinstance(minute, int) or isinstance(minute, bool) or not 0 <= minute <= 130:
        raise MatchErrors.InvalidMinute
    return normalized_player_name
