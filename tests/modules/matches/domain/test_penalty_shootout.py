from uuid import uuid4

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
    squad_players = {}

    for team_side, team_id, shirt_number in (
        (TeamSide.HOME, match.home_team_id, 9),
        (TeamSide.AWAY, match.away_team_id, 10),
    ):
        player = Player.create(team_id=team_id, name=f"Lanzador {team_side}")
        squad_players[team_side] = MatchSquadPlayer.create(
            match=match,
            player=player,
            team_side=team_side,
            shirt_number=shirt_number,
        )

    return match, shootout, squad_players


def record_kick(shootout, squad_players, outcome):
    team_side = shootout.next_team_side or TeamSide.HOME
    squad_player = squad_players[team_side]
    previous_kick_count = (
        shootout.home_kick_count if team_side == TeamSide.HOME else shootout.away_kick_count
    )

    return PenaltyShootoutKick.create(
        shootout=shootout,
        squad_player=squad_player,
        sequence_number=shootout.home_kick_count + shootout.away_kick_count + 1,
        outcome=outcome,
        eligible_player_ids={squad_player.player_id},
        kick_counts={squad_player.player_id: previous_kick_count},
    )


def decide_early_for_home(shootout, squad_players):
    for outcome in (
        PenaltyKickOutcome.SCORED,
        PenaltyKickOutcome.MISSED,
        PenaltyKickOutcome.SCORED,
        PenaltyKickOutcome.MISSED,
        PenaltyKickOutcome.SCORED,
        PenaltyKickOutcome.MISSED,
    ):
        record_kick(shootout, squad_players, outcome)


def test_records_scored_kick_without_changing_match_score():
    match, shootout, squad_players = create_shootout()

    kick = record_kick(shootout, squad_players, PenaltyKickOutcome.SCORED)

    assert kick.player_name == "Lanzador home"
    assert shootout.home_score == 1
    assert shootout.away_score == 0
    assert shootout.home_kick_count == 1
    assert shootout.next_team_side == TeamSide.AWAY
    assert match.home_goal_count == 0


def test_allows_away_team_to_take_the_first_kick():
    match, _, squad_players = create_shootout()
    shootout = PenaltyShootout.start(
        match=match,
        starting_team_side=TeamSide.AWAY,
    )

    kick = record_kick(shootout, squad_players, PenaltyKickOutcome.SCORED)

    assert kick.team_side == TeamSide.AWAY
    assert shootout.next_team_side == TeamSide.HOME


def test_rejects_repeated_kicker_until_every_eligible_player_has_kicked():
    first_player_id = uuid4()
    second_player_id = uuid4()

    with pytest.raises(type(MatchErrors.PenaltyShootoutKickerAlreadyUsed)):
        PenaltyShootout.ensure_kicker_rotation(
            player_id=first_player_id,
            eligible_player_ids={first_player_id, second_player_id},
            kick_counts={first_player_id: 1},
        )


def test_allows_kicker_to_repeat_after_every_eligible_player_has_kicked():
    first_player_id = uuid4()
    second_player_id = uuid4()

    PenaltyShootout.ensure_kicker_rotation(
        player_id=first_player_id,
        eligible_player_ids={first_player_id, second_player_id},
        kick_counts={first_player_id: 1, second_player_id: 1},
    )


def test_decides_winner_early_when_opponent_cannot_equal_score():
    _, shootout, squad_players = create_shootout()

    decide_early_for_home(shootout, squad_players)

    assert shootout.status == PenaltyShootoutStatus.DECIDED
    assert shootout.winner_team_side == TeamSide.HOME
    assert shootout.home_kick_count == 3
    assert shootout.away_kick_count == 3
    assert shootout.next_team_side is None


def test_uses_sudden_death_after_five_tied_rounds():
    _, shootout, squad_players = create_shootout()

    for _ in range(10):
        record_kick(shootout, squad_players, PenaltyKickOutcome.SCORED)

    assert shootout.status == PenaltyShootoutStatus.IN_PROGRESS

    record_kick(shootout, squad_players, PenaltyKickOutcome.SCORED)
    assert shootout.status == PenaltyShootoutStatus.IN_PROGRESS

    record_kick(shootout, squad_players, PenaltyKickOutcome.MISSED)
    assert shootout.status == PenaltyShootoutStatus.DECIDED
    assert shootout.winner_team_side == TeamSide.HOME


def test_rejects_kick_after_winner_is_decided():
    _, shootout, squad_players = create_shootout()
    decide_early_for_home(shootout, squad_players)

    with pytest.raises(type(MatchErrors.PenaltyShootoutAlreadyDecided)):
        record_kick(shootout, squad_players, PenaltyKickOutcome.SCORED)


def test_finishes_decided_shootout():
    _, shootout, squad_players = create_shootout()
    decide_early_for_home(shootout, squad_players)

    shootout.finish()

    assert shootout.status == PenaltyShootoutStatus.FINISHED


def test_rejects_finishing_undecided_shootout():
    _, shootout, _ = create_shootout()

    with pytest.raises(type(MatchErrors.PenaltyShootoutNotDecided)):
        shootout.finish()
