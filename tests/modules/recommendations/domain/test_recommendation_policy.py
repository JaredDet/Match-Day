from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from modules.recommendations.domain.content_reference import (
    ContentKind,
    ContentReference,
    RecommendationContent,
)
from modules.recommendations.domain.navigation_activity import NavigationActivity
from modules.recommendations.domain.recommendation_policy import (
    InterestWeights,
    RecommendationPolicy,
)
from modules.recommendations.errors import RecommendationErrors


def test_visits_decay_by_half_after_seven_days():
    now = datetime(2026, 9, 21, 12, tzinfo=UTC)
    team_id = uuid4()
    content = RecommendationContent(
        ContentReference(ContentKind.TEAM, team_id), "Team", "/team", "", (team_id,)
    )
    activity = NavigationActivity(
        content_kind=ContentKind.TEAM,
        content_id=team_id,
        occurred_at=now - timedelta(days=7),
        counts_as_visit=True,
    )
    profile = RecommendationPolicy.profile([activity], {content.reference.key: content}, now)
    assert profile.teams[str(team_id)] == pytest.approx(0.5)


def test_player_visits_propagate_to_the_team_but_players_are_not_feed_items():
    now = datetime(2026, 9, 21, 12, tzinfo=UTC)
    team_id, player_id = uuid4(), uuid4()
    player = RecommendationContent(
        ContentReference(ContentKind.PLAYER, player_id), "Player", "/player", "", (team_id,)
    )
    activity = NavigationActivity(
        content_kind=ContentKind.PLAYER, content_id=player_id, occurred_at=now
    )
    profile = RecommendationPolicy.profile([activity], {player.reference.key: player}, now)
    assert profile.teams[str(team_id)] == 1
    assert all(
        not items for items in RecommendationPolicy.recommend([player], profile, now).values()
    )


def test_discovery_prefers_unseen_content_outside_inferred_interests():
    now = datetime(2026, 9, 21, 12, tzinfo=UTC)
    first, second = uuid4(), uuid4()
    items = [
        RecommendationContent(ContentReference(ContentKind.TEAM, id), str(id), "/team", "", (id,))
        for id in (first, second)
    ]
    profile = InterestWeights({str(first): 5}, {}, frozenset({items[0].reference.key}))
    result = RecommendationPolicy.recommend(items, profile, now)
    assert [item["id"] for item in result["discovery"]] == [str(second)]
    assert result["discovery"][0]["reason"] == "discovery"


@pytest.mark.parametrize("seconds", [True, -1, 121, 30.5])
def test_domain_rejects_invalid_active_time(seconds):
    now = datetime(2026, 9, 21, 12, tzinfo=UTC)
    activity = NavigationActivity(occurred_at=now - timedelta(minutes=5))
    with pytest.raises(type(RecommendationErrors.InvalidActiveTime)) as error:
        activity.accumulate_active_time(seconds, now)
    assert error.value.code == RecommendationErrors.InvalidActiveTime.code


def test_navigation_limits_belong_to_domain_and_include_midnight_cooldown():
    from modules.recommendations.domain.navigation_policy import NavigationCounts, NavigationPolicy

    now = datetime(2026, 9, 22, 0, 5, tzinfo=UTC)
    assert not NavigationPolicy.can_record(NavigationCounts(200, 0, None))
    assert NavigationPolicy.can_record(NavigationCounts(199, 0, None))
    assert not NavigationPolicy.counts_as_visit(NavigationCounts(3, 3, None), now)
    assert not NavigationPolicy.counts_as_visit(
        NavigationCounts(0, 0, now - timedelta(minutes=10)), now
    )
    assert NavigationPolicy.counts_as_visit(
        NavigationCounts(0, 0, now - timedelta(minutes=31)), now
    )
