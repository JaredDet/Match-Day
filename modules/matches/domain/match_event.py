from django.db import models

from modules.matches.constants import (
    EXTRA_TIME_FIRST_HALF_END_MINUTE,
    EXTRA_TIME_FIRST_HALF_START_MINUTE,
    EXTRA_TIME_SECOND_HALF_START_MINUTE,
    FIRST_HALF_END_MINUTE,
    MAX_MATCH_MINUTE,
    MIN_MATCH_MINUTE,
    SECOND_HALF_END_MINUTE,
    SECOND_HALF_START_MINUTE,
)
from modules.matches.errors import MatchErrors


class TeamSide(models.TextChoices):
    HOME = "home"
    AWAY = "away"


class MatchPeriod(models.TextChoices):
    FIRST_HALF = "first_half"
    HALFTIME = "halftime"
    SECOND_HALF = "second_half"
    EXTRA_TIME_FIRST_HALF = "extra_time_first_half"
    EXTRA_TIME_HALFTIME = "extra_time_halftime"
    EXTRA_TIME_SECOND_HALF = "extra_time_second_half"


def timed_match_event_constraints(prefix: str) -> list[models.CheckConstraint]:
    return [
        models.CheckConstraint(
            condition=models.Q(team_side__in=TeamSide.values),
            name=f"valid_{prefix}_team_side",
        ),
        models.CheckConstraint(
            condition=models.Q(
                minute__gte=MIN_MATCH_MINUTE,
                minute__lte=MAX_MATCH_MINUTE,
            ),
            name=f"valid_{prefix}_minute",
        ),
        models.CheckConstraint(
            condition=(
                models.Q(
                    period=MatchPeriod.FIRST_HALF,
                    minute__gte=MIN_MATCH_MINUTE,
                    minute__lte=FIRST_HALF_END_MINUTE,
                )
                | models.Q(
                    period=MatchPeriod.SECOND_HALF,
                    minute__gte=SECOND_HALF_START_MINUTE,
                    minute__lte=SECOND_HALF_END_MINUTE,
                )
                | models.Q(
                    period=MatchPeriod.EXTRA_TIME_FIRST_HALF,
                    minute__gte=EXTRA_TIME_FIRST_HALF_START_MINUTE,
                    minute__lte=EXTRA_TIME_FIRST_HALF_END_MINUTE,
                )
                | models.Q(
                    period=MatchPeriod.EXTRA_TIME_SECOND_HALF,
                    minute__gte=EXTRA_TIME_SECOND_HALF_START_MINUTE,
                    minute__lte=MAX_MATCH_MINUTE,
                )
            ),
            name=f"valid_{prefix}_period_minute",
        ),
        models.CheckConstraint(
            condition=models.Q(added_minute=0)
            | models.Q(period=MatchPeriod.FIRST_HALF, minute=FIRST_HALF_END_MINUTE)
            | models.Q(period=MatchPeriod.SECOND_HALF, minute=SECOND_HALF_END_MINUTE)
            | models.Q(
                period=MatchPeriod.EXTRA_TIME_FIRST_HALF,
                minute=EXTRA_TIME_FIRST_HALF_END_MINUTE,
            )
            | models.Q(
                period=MatchPeriod.EXTRA_TIME_SECOND_HALF,
                minute=MAX_MATCH_MINUTE,
            ),
            name=f"valid_{prefix}_added_minute",
        ),
    ]


def validate_match_event(
    team_side: TeamSide,
    period: MatchPeriod,
    minute: int,
    added_minute: int = 0,
) -> None:
    if not isinstance(team_side, TeamSide):
        raise MatchErrors.InvalidTeamSide
    validate_match_clock(period, minute, added_minute)


def validate_match_clock(
    period: MatchPeriod,
    minute: int,
    added_minute: int = 0,
) -> None:
    if not isinstance(period, MatchPeriod) or period in {
        MatchPeriod.HALFTIME,
        MatchPeriod.EXTRA_TIME_HALFTIME,
    }:
        raise MatchErrors.InvalidPeriod
    if not isinstance(minute, int) or isinstance(minute, bool):
        raise MatchErrors.InvalidMinute
    valid_minute = (
        (period == MatchPeriod.FIRST_HALF and MIN_MATCH_MINUTE <= minute <= FIRST_HALF_END_MINUTE)
        or (
            period == MatchPeriod.SECOND_HALF
            and SECOND_HALF_START_MINUTE <= minute <= SECOND_HALF_END_MINUTE
        )
        or (
            period == MatchPeriod.EXTRA_TIME_FIRST_HALF
            and EXTRA_TIME_FIRST_HALF_START_MINUTE <= minute <= EXTRA_TIME_FIRST_HALF_END_MINUTE
        )
        or (
            period == MatchPeriod.EXTRA_TIME_SECOND_HALF
            and EXTRA_TIME_SECOND_HALF_START_MINUTE <= minute <= MAX_MATCH_MINUTE
        )
    )
    if not valid_minute:
        raise MatchErrors.InvalidMinute
    if (
        not isinstance(added_minute, int)
        or isinstance(added_minute, bool)
        or added_minute < 0
        or (
            added_minute > 0
            and minute
            not in (
                FIRST_HALF_END_MINUTE,
                SECOND_HALF_END_MINUTE,
                EXTRA_TIME_FIRST_HALF_END_MINUTE,
                MAX_MATCH_MINUTE,
            )
        )
    ):
        raise MatchErrors.InvalidAddedMinute
