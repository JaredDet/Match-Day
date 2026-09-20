from types import SimpleNamespace
from uuid import UUID

from modules.tournaments.domain.standings import rank_group


def match(home, away, home_score, away_score, home_yellow=0, away_red=0):
    return SimpleNamespace(
        home_team_id=home,
        away_team_id=away,
        home_goal_count=home_score,
        away_goal_count=away_score,
        home_yellow_card_count=home_yellow,
        away_yellow_card_count=0,
        home_red_card_count=0,
        away_red_card_count=away_red,
    )


def test_head_to_head_breaks_equal_overall_points_goal_difference_and_goals():
    a, b, c, d = [UUID(int=i) for i in (4, 3, 2, 1)]
    matches = [
        match(a, b, 1, 0),
        match(c, a, 1, 0),
        match(b, c, 1, 0),
        match(a, d, 2, 0),
        match(b, d, 2, 0),
        match(c, d, 3, 0),
    ]

    rows = rank_group([a, b, c, d], matches, [])

    assert [row[0] for row in rows] == [c, a, b, d]
    assert all(not row[2] for row in rows)


def test_discipline_precedes_registered_draw_order():
    a, b = UUID(int=1), UUID(int=2)

    rows = rank_group([a, b], [match(a, b, 0, 0, home_yellow=1)], [str(a), str(b)])

    assert rows[0][0] == b
    assert not rows[0][2]


def test_red_card_costs_three_yellow_cards():
    a, b = UUID(int=1), UUID(int=2)

    rows = rank_group([a, b], [match(a, b, 0, 0, home_yellow=2, away_red=1)], [])

    assert rows[0][0] == a
    assert not rows[0][2]


def test_unresolved_tie_is_visible_until_full_manual_order_is_recorded():
    a, b = UUID(int=1), UUID(int=2)
    matches = [match(a, b, 1, 1)]

    assert all(row[2] for row in rank_group([a, b], matches, []))
    assert all(row[2] for row in rank_group([a, b], matches, [str(a)]))

    resolved = rank_group([a, b], matches, [str(b), str(a)])

    assert [row[0] for row in resolved] == [b, a]
    assert all(not row[2] for row in resolved)
