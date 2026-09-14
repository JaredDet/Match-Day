from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.db import models

from modules.matches.constants import (
    EXTRA_TIME_FIRST_HALF_END_MINUTE,
    EXTRA_TIME_FIRST_HALF_START_MINUTE,
    EXTRA_TIME_SECOND_HALF_START_MINUTE,
    FIRST_HALF_END_MINUTE,
    MAX_MATCH_MINUTE,
    SECOND_HALF_END_MINUTE,
    SECOND_HALF_START_MINUTE,
)
from modules.matches.domain.match_event import MatchPeriod

SECONDS_PER_MINUTE = 60
REGULATION_HALF_SECONDS = 45 * SECONDS_PER_MINUTE
EXTRA_TIME_HALF_SECONDS = 15 * SECONDS_PER_MINUTE


class MatchClockStatus(models.TextChoices):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    REGULATION_TIME_REACHED = "regulation_time_reached"
    DEADLINE_REACHED = "deadline_reached"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class MatchClockSnapshot:
    period: MatchPeriod | None
    status: MatchClockStatus
    minute: int | None
    second: int
    added_minute: int
    elapsed_seconds: int
    remaining_seconds: int | None
    deadline_at: datetime | None
    announced_added_minutes: int
    version: int
    as_of: datetime


def period_clock_values(period: MatchPeriod) -> tuple[int, int, int]:
    values = {
        MatchPeriod.FIRST_HALF: (0, FIRST_HALF_END_MINUTE, REGULATION_HALF_SECONDS),
        MatchPeriod.SECOND_HALF: (
            SECOND_HALF_START_MINUTE - 1,
            SECOND_HALF_END_MINUTE,
            REGULATION_HALF_SECONDS,
        ),
        MatchPeriod.EXTRA_TIME_FIRST_HALF: (
            EXTRA_TIME_FIRST_HALF_START_MINUTE - 1,
            EXTRA_TIME_FIRST_HALF_END_MINUTE,
            EXTRA_TIME_HALF_SECONDS,
        ),
        MatchPeriod.EXTRA_TIME_SECOND_HALF: (
            EXTRA_TIME_SECOND_HALF_START_MINUTE - 1,
            MAX_MATCH_MINUTE,
            EXTRA_TIME_HALF_SECONDS,
        ),
    }
    return values[period]
