import pytest

from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import MatchSquadPlayer
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootout,
    PenaltyShootoutKick,
    PenaltyShootoutStatus,
)
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother


def create_shootout():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
        current_minute=90,
    )
    shootout = PenaltyShootout.start(match=match)
    player = Player.create(team_id=match.home_team_id, name="Lanzador")
    squad_player = MatchSquadPlayer.create(
        match=match,
        player=player,
        team_side=TeamSide.HOME,
        shirt_number=9,
    )

    return match, shootout, squad_player


def test_records_scored_kick_without_changing_match_score():
    match, shootout, squad_player = create_shootout()

    kick = PenaltyShootoutKick.create(
        shootout=shootout,
        squad_player=squad_player,
        sequence_number=1,
        outcome=PenaltyKickOutcome.SCORED,
    )

    assert kick.player_name == "Lanzador"
    assert shootout.home_score == 1
    assert shootout.away_score == 0
    assert match.home_goal_count == 0


def test_finishes_shootout_with_winner():
    _, shootout, squad_player = create_shootout()
    PenaltyShootoutKick.create(
        shootout=shootout,
        squad_player=squad_player,
        sequence_number=1,
        outcome=PenaltyKickOutcome.SCORED,
    )

    shootout.finish()

    assert shootout.status == PenaltyShootoutStatus.FINISHED
    assert shootout.winner_team_side == TeamSide.HOME


def test_rejects_finishing_tied_shootout():
    _, shootout, _ = create_shootout()

    with pytest.raises(type(MatchErrors.PenaltyShootoutIsTied)):
        shootout.finish()
