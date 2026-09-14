from importlib import import_module

import pytest
from django.apps import apps

from modules.matches.domain.card import CardType
from modules.matches.domain.goal import GoalType
from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.penalty_attempt import PenaltyAttemptOutcome
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_backfills_shots_on_target_and_saves_from_existing_events():
    match = MatchMother.create(
        persist_teams=True,
        status=MatchStatus.LIVE,
    )
    match.save()
    home_player = Player.objects.create(team=match.home_team, name="Local")
    away_player = Player.objects.create(team=match.away_team, name="Visitante")

    goal = match.register_goal(player=home_player, minute=60)
    saved_penalty = match.register_penalty_attempt(
        player=away_player,
        outcome=PenaltyAttemptOutcome.SAVED,
        minute=61,
    )
    own_goal = match.register_goal(
        player=away_player,
        goal_type=GoalType.OWN_GOAL,
        minute=62,
    )
    disallowed_goal = match.register_goal(player=away_player, minute=63)
    match.disallow_goal(disallowed_goal)
    match.save()
    goal.save()
    saved_penalty.save()
    own_goal.save()
    disallowed_goal.save()

    Match.objects.filter(id=match.id).update(
        home_shot_count=0,
        away_shot_count=0,
        home_shot_on_target_count=0,
        away_shot_on_target_count=0,
        home_save_count=0,
        away_save_count=0,
    )

    migration = import_module(
        "modules.matches.migrations."
        "0033_cornerkick_foul_offside_shot_match_away_corner_count_and_more"
    )
    migration.backfill_match_statistics(apps, None)
    match.refresh_from_db()

    assert match.home_shot_count == 1
    assert match.home_shot_on_target_count == 1
    assert match.home_save_count == 1
    assert match.away_shot_count == 1
    assert match.away_shot_on_target_count == 1
    assert match.away_save_count == 0


def test_backfills_card_statistics_excluding_rescinded_cards():
    match = MatchMother.create(
        persist_teams=True,
        status=MatchStatus.LIVE,
    )
    match.save()
    home_player = Player.objects.create(team=match.home_team, name="Local")
    away_player = Player.objects.create(team=match.away_team, name="Visitante")

    yellow = match.register_card(
        player=home_player,
        card_type=CardType.YELLOW,
        minute=60,
    )
    red = match.register_card(
        player=away_player,
        card_type=CardType.RED,
        minute=61,
    )
    rescinded = match.register_card(
        player=home_player,
        card_type=CardType.YELLOW,
        minute=62,
    )
    match.rescind_card(rescinded)
    match.save()
    yellow.save()
    red.save()
    rescinded.save()

    Match.objects.filter(id=match.id).update(
        home_yellow_card_count=0,
        away_yellow_card_count=0,
        home_red_card_count=0,
        away_red_card_count=0,
    )

    migration = import_module(
        "modules.matches.migrations.0034_match_away_red_card_count_and_more"
    )
    migration.backfill_card_statistics(apps, None)
    match.refresh_from_db()

    assert match.home_yellow_card_count == 1
    assert match.away_yellow_card_count == 0
    assert match.home_red_card_count == 0
    assert match.away_red_card_count == 1
