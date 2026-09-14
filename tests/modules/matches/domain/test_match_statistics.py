import pytest

from modules.matches.domain.goal import GoalType
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.domain.penalty_attempt import PenaltyAttemptOutcome
from modules.matches.domain.shot import ShotOutcome
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother


def test_registers_statistical_events_and_updates_counters():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
        current_minute=30,
    )
    home_player = Player.create(team_id=match.home_team_id, name="Delantero")
    away_goalkeeper = Player.create(team_id=match.away_team_id, name="Arquero")

    match.register_foul(player=home_player, minute=10)
    match.register_corner_kick(player=home_player, minute=11)
    match.register_offside(player=home_player, minute=12)
    shot = match.register_shot(
        player=home_player,
        goalkeeper=away_goalkeeper,
        outcome=ShotOutcome.SAVED,
        minute=13,
    )
    match.update_possession(58)

    assert shot.goalkeeper_name == "Arquero"
    assert match.home_foul_count == 1
    assert match.home_corner_count == 1
    assert match.home_offside_count == 1
    assert match.home_shot_count == 1
    assert match.home_shot_on_target_count == 1
    assert match.away_save_count == 1
    assert match.home_possession_percentage == 58


def test_rejects_saved_shot_without_opponent_goalkeeper():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
        current_minute=30,
    )
    player = Player.create(team_id=match.home_team_id, name="Delantero")

    with pytest.raises(type(MatchErrors.InvalidShotGoalkeeper)):
        match.register_shot(
            player=player,
            outcome=ShotOutcome.SAVED,
            minute=13,
        )


@pytest.mark.parametrize(
    ("outcome", "expected_on_target", "expected_saves"),
    [
        (ShotOutcome.OFF_TARGET, 0, 0),
        (ShotOutcome.BLOCKED, 0, 0),
        (ShotOutcome.WOODWORK, 0, 0),
        (ShotOutcome.SAVED, 1, 1),
    ],
)
def test_updates_counters_for_every_shot_outcome(
    outcome,
    expected_on_target,
    expected_saves,
):
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
        current_minute=30,
    )
    shooter = Player.create(team_id=match.home_team_id, name="Delantero")
    goalkeeper = Player.create(team_id=match.away_team_id, name="Arquero")

    match.register_shot(
        player=shooter,
        goalkeeper=goalkeeper if outcome == ShotOutcome.SAVED else None,
        outcome=outcome,
        minute=20,
    )

    assert match.home_shot_count == 1
    assert match.home_shot_on_target_count == expected_on_target
    assert match.away_save_count == expected_saves


def test_rejects_saved_shot_with_goalkeeper_from_shooters_team():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
        current_minute=30,
    )
    shooter = Player.create(team_id=match.home_team_id, name="Delantero")
    goalkeeper = Player.create(team_id=match.home_team_id, name="Arquero")

    with pytest.raises(type(MatchErrors.InvalidShotGoalkeeper)):
        match.register_shot(
            player=shooter,
            goalkeeper=goalkeeper,
            outcome=ShotOutcome.SAVED,
            minute=20,
        )


@pytest.mark.parametrize("goal_type", [GoalType.REGULAR, GoalType.PENALTY])
def test_goal_counts_as_shot_on_target_and_disallowing_it_reverts_counters(goal_type):
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Delantero")

    goal = match.register_goal(player=player, goal_type=goal_type, minute=60)

    assert match.home_shot_count == 1
    assert match.home_shot_on_target_count == 1

    match.disallow_goal(goal)

    assert match.home_shot_count == 0
    assert match.home_shot_on_target_count == 0


def test_own_goal_does_not_count_as_attacking_shot():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Defensor")

    match.register_goal(player=player, goal_type=GoalType.OWN_GOAL, minute=60)

    assert match.home_shot_count == 0
    assert match.away_shot_count == 0


@pytest.mark.parametrize(
    ("outcome", "expected_on_target", "expected_saves"),
    [
        (PenaltyAttemptOutcome.MISSED, 0, 0),
        (PenaltyAttemptOutcome.HIT_POST, 0, 0),
        (PenaltyAttemptOutcome.SAVED, 1, 1),
    ],
)
def test_non_converted_penalty_updates_shot_statistics(
    outcome,
    expected_on_target,
    expected_saves,
):
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Delantero")

    match.register_penalty_attempt(player=player, outcome=outcome, minute=60)

    assert match.home_shot_count == 1
    assert match.home_shot_on_target_count == expected_on_target
    assert match.away_save_count == expected_saves


@pytest.mark.parametrize("percentage", [-1, 101, True])
def test_rejects_invalid_possession(percentage):
    match = MatchMother.create(status=MatchStatus.LIVE)

    with pytest.raises(type(MatchErrors.InvalidPossession)):
        match.update_possession(percentage)
