import uuid

import pytest

from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal, GoalType
from modules.matches.domain.injury import Injury
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.penalty_attempt import PenaltyAttempt, PenaltyAttemptOutcome
from modules.matches.domain.var_review import VarReview, VarReviewDecision, VarReviewReason
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from tests.mothers.matches.match_mother import MatchMother


def test_registers_goal_with_player_snapshot_during_live_match():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
    )
    player = Player.create(team_id=match.home_team_id, name="Goleador Local")
    event_id = uuid.uuid4()

    goal = match.register_goal(event_id=event_id, player=player, minute=34)
    player.rename("Nombre posterior")

    assert isinstance(goal, Goal)
    assert goal.id == event_id
    assert goal.player == player
    assert goal.player_name == "Goleador Local"
    assert goal.team_side == TeamSide.HOME
    assert match.home_goal_count == 1


def test_registers_card_and_derives_away_side():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.away_team_id, name="Defensor Visitante")

    card = match.register_card(player=player, card_type=CardType.YELLOW, minute=51)

    assert isinstance(card, Card)
    assert card.player == player
    assert card.player_name == "Defensor Visitante"
    assert card.team_side == TeamSide.AWAY
    assert match.away_card_count == 1
    assert match.away_yellow_card_count == 1
    assert match.away_red_card_count == 0


def test_registers_own_goal_for_opposing_team():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Defensor local")

    goal = match.register_goal(
        player=player,
        goal_type=GoalType.OWN_GOAL,
        minute=50,
    )

    assert goal.team_side == TeamSide.AWAY
    assert match.home_goal_count == 0
    assert match.away_goal_count == 1

    match.disallow_goal(goal)

    assert match.away_goal_count == 0


def test_registers_goal_with_assistant_snapshot():
    match = MatchMother.create(status=MatchStatus.LIVE)
    scorer = Player.create(team_id=match.home_team_id, name="Goleador")
    assistant = Player.create(team_id=match.home_team_id, name="Asistente")

    goal = match.register_goal(
        player=scorer,
        assist_player=assistant,
        minute=60,
    )
    assistant.rename("Nombre posterior")

    assert goal.assist_player == assistant
    assert goal.assist_player_name == "Asistente"


@pytest.mark.parametrize("goal_type", [GoalType.PENALTY, GoalType.OWN_GOAL])
def test_rejects_assistance_for_goal_types_without_assist(goal_type):
    match = MatchMother.create(status=MatchStatus.LIVE)
    scorer = Player.create(team_id=match.home_team_id, name="Goleador")
    assistant = Player.create(team_id=match.home_team_id, name="Asistente")

    with pytest.raises(type(MatchErrors.InvalidGoalAssist)):
        match.register_goal(
            player=scorer,
            assist_player=assistant,
            goal_type=goal_type,
            minute=60,
        )


def test_registers_penalty_attempt_injury_and_var_review():
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Jugador")
    reviewed_event_id = uuid.uuid4()

    penalty_attempt = match.register_penalty_attempt(
        player=player,
        outcome=PenaltyAttemptOutcome.SAVED,
        minute=55,
    )
    injury = match.register_injury(player=player, minute=60)
    var_review = match.register_var_review(
        team_side=TeamSide.HOME,
        reason=VarReviewReason.PENALTY,
        decision=VarReviewDecision.CONFIRMED,
        reviewed_event_id=reviewed_event_id,
        minute=61,
    )

    assert isinstance(penalty_attempt, PenaltyAttempt)
    assert penalty_attempt.outcome == PenaltyAttemptOutcome.SAVED
    assert isinstance(injury, Injury)
    assert injury.player_name == "Jugador"
    assert isinstance(var_review, VarReview)
    assert var_review.reviewed_event_id == reviewed_event_id


def test_registers_first_half_added_time_without_changing_official_minute():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
    )
    player = Player.create(team_id=match.home_team_id, name="Goleador")
    match.update_clock(
        expected_period=MatchPeriod.FIRST_HALF,
        minute=45,
        added_minute=3,
    )

    goal = match.register_goal(player=player, minute=45, added_minute=3)

    assert goal.period == MatchPeriod.FIRST_HALF
    assert goal.minute == 45
    assert goal.added_minute == 3


def test_rejects_added_time_outside_end_of_period():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )
    player = Player.create(team_id=match.home_team_id, name="Goleador")

    with pytest.raises(type(MatchErrors.InvalidAddedMinute)):
        match.register_goal(player=player, minute=80, added_minute=2)


def test_rejects_event_ahead_of_match_clock():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
        current_minute=20,
    )
    player = Player.create(team_id=match.home_team_id, name="Goleador")

    with pytest.raises(type(MatchErrors.EventAheadOfClock)):
        match.register_goal(player=player, minute=21)


@pytest.mark.parametrize("status", [MatchStatus.SCHEDULED, MatchStatus.FINISHED])
def test_rejects_event_when_match_is_not_live(status):
    match = MatchMother.create(status=status)
    player = Player.create(team_id=match.home_team_id, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidState)):
        match.register_goal(player=player, minute=1)


def test_rejects_player_from_team_outside_match():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
    )
    player = Player.create(team_id=Team.create(name="Otro equipo").id, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidPlayerTeam)) as exc_info:
        match.register_goal(player=player, minute=10)

    assert exc_info.value.code == "invalid_player_team"


@pytest.mark.parametrize("minute", [-1, 131, True])
def test_rejects_invalid_event_minute(minute):
    match = MatchMother.create(status=MatchStatus.LIVE)
    player = Player.create(team_id=match.home_team_id, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidMinute)):
        match.register_goal(player=player, minute=minute)


def test_rejects_invalid_card_type():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.FIRST_HALF,
    )
    player = Player.create(team_id=match.home_team_id, name="Jugador")

    with pytest.raises(type(MatchErrors.InvalidCardType)):
        match.register_card(player=player, card_type="blue", minute=15)
