from modules.recommendations.domain.collaborative_policy import CollaborativePolicy


def test_shared_behavior_discovers_unseen_content_with_two_supporters():
    result = CollaborativePolicy.recommend(
        {"team:a": 1, "team:b": 1},
        {
            "one": {"team:a": 1, "team:b": 1, "news:new": 1},
            "two": {"team:a": 2, "team:b": 2, "news:new": 2},
        },
    )
    assert set(result) == {"news:new"}
    assert 0 < result["news:new"] <= 2


def test_single_neighbor_unrelated_visitors_and_empty_history_do_not_create_suggestions():
    peers = {"one": {"a": 1, "b": 1, "new": 1}}
    assert CollaborativePolicy.recommend({"a": 1, "b": 1}, peers) == {}
    assert CollaborativePolicy.recommend({}, peers) == {}
    assert CollaborativePolicy.recommend({"unrelated": 1}, peers) == {}


def test_one_shared_content_and_zero_weight_signals_are_insufficient():
    peers = {"one": {"a": 1, "b": 0, "new": 1}, "two": {"a": 1, "b": 0, "new": 1}}
    assert CollaborativePolicy.recommend({"a": 1, "b": 1}, peers) == {}


def test_multiplying_a_neighbors_activity_does_not_increase_their_influence():
    first = {"a": 1, "b": 2, "new": 3}
    result = CollaborativePolicy.recommend({"a": 1, "b": 1}, {"one": first, "two": first})
    multiplied = {key: value * 100 for key, value in first.items()}
    scaled = CollaborativePolicy.recommend({"a": 1, "b": 1}, {"one": multiplied, "two": multiplied})
    assert abs(result["new"] - scaled["new"]) < 0.000001
