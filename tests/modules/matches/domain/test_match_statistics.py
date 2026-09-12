import pytest

from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod
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


@pytest.mark.parametrize("percentage", [-1, 101, True])
def test_rejects_invalid_possession(percentage):
    match = MatchMother.create(status=MatchStatus.LIVE)

    with pytest.raises(type(MatchErrors.InvalidPossession)):
        match.update_possession(percentage)
