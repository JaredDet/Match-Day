from uuid import uuid4

import pytest

from modules.matches.domain.card import CardType
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_builds_chronological_match_detail_without_cancelled_events():
    match = MatchMother.create(status=MatchStatus.LIVE)
    late_goal = match.register_goal(
        team_side=TeamSide.HOME,
        player_name="Goleador",
        minute=60,
    )
    early_card = match.register_card(
        team_side=TeamSide.AWAY,
        player_name="Defensor",
        card_type=CardType.YELLOW,
        minute=20,
    )
    cancelled_goal = match.register_goal(
        team_side=TeamSide.AWAY,
        player_name="Gol anulado",
        minute=10,
    )
    match.cancel_goal(cancelled_goal)
    match.save()
    late_goal.save()
    early_card.save()
    cancelled_goal.save()

    result = MatchQueryRepository().get(match.id)

    assert result.home_team.name == match.home_team_name
    assert result.home_team.goals == 1
    assert result.away_team.goals == 0
    assert [event.type for event in result.events] == ["yellow_card", "goal"]
    assert [event.minute for event in result.events] == [20, 60]


def test_returns_none_when_match_does_not_exist():
    assert MatchQueryRepository().get(uuid4()) is None
