from io import StringIO

import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.domain.penalty_shootout import PenaltyShootoutStatus
from modules.matches.management.commands.seed_demo_match import find_demo_match
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_seeds_complete_demo_dataset_and_is_idempotent():
    output = StringIO()

    call_command("seed_demo_match", stdout=output)
    call_command("seed_demo_match", stdout=output)

    match = find_demo_match()
    assert match is not None
    assert Team.objects.count() == 4
    assert Player.objects.count() == 64
    assert Match.objects.count() == 13
    assert Match.objects.filter(status=MatchStatus.FINISHED).count() == 6
    assert Match.objects.filter(status=MatchStatus.SCHEDULED).count() == 4
    assert (
        Match.objects.filter(
            status=MatchStatus.LIVE,
            current_period=MatchPeriod.FIRST_HALF,
            current_minute=34,
        ).count()
        == 1
    )
    assert (
        Match.objects.filter(
            status=MatchStatus.LIVE,
            current_period=MatchPeriod.HALFTIME,
            current_minute=45,
        ).count()
        == 1
    )
    assert (
        Match.objects.filter(
            status=MatchStatus.LIVE,
            current_period=MatchPeriod.SECOND_HALF,
            current_minute=72,
        ).count()
        == 1
    )
    assert Match.objects.filter(id=match.id).count() == 1
    assert match.status == MatchStatus.FINISHED
    assert match.home_team_name == "Atlético del Puerto"
    assert match.home_team.name == "Atlético Bahía"
    assert match.stadium_name == "Estadio del Horizonte"
    assert match.referee_name == "Alex Rivera"
    assert match.home_goal_count == 2
    assert match.away_goal_count == 1
    assert match.squad_players.count() == 32
    assert match.squad_players.filter(role="starter").count() == 22
    assert match.squad_players.filter(role="substitute").count() == 10
    assert match.squad_players.filter(player__name="Mateo Rojas").exists()
    assert match.squad_players.filter(player__name="Franco Bustos").exists()
    assert not match.squad_players.filter(player__name__startswith="Jugador ").exists()
    assert match.goals.filter(disallowed_at__isnull=True).count() == 3
    assert match.goals.filter(disallowed_at__isnull=False).count() == 1
    assert match.substitutions.count() == 2
    assert match.cards.filter(rescinded_at__isnull=True).count() == 3
    assert match.cards.filter(rescinded_at__isnull=False).count() == 1
    assert match.goals.filter(player_name="Lucas Contreras").exists()
    assert match.cards.filter(player_name="Ignacio Silva").exists()

    shootout_match = Match.objects.get(penalty_shootout__isnull=False)
    assert shootout_match.current_period == MatchPeriod.EXTRA_TIME_SECOND_HALF
    assert shootout_match.current_minute == 120
    assert shootout_match.home_goal_count == shootout_match.away_goal_count
    assert shootout_match.penalty_shootout.status == PenaltyShootoutStatus.FINISHED
    assert shootout_match.penalty_shootout.home_score == 4
    assert shootout_match.penalty_shootout.away_score == 3
    assert shootout_match.penalty_shootout.kicks.count() == 8

    response = APIClient().get(reverse("matches-detail", args=[shootout_match.id]))
    assert response.status_code == 200
    assert response.data["home_team"]["penalty_score"] == 4
    assert response.data["away_team"]["penalty_score"] == 3
    assert response.data["penalty_shootout"]["winner_team_side"] == "home"
    assert len(response.data["penalty_shootout"]["kicks"]) == 8

    list_response = APIClient().get(reverse("matches-list"))
    primary_summary = next(item for item in list_response.data if item["id"] == str(match.id))
    penalty_goal = next(
        goal for goal in primary_summary["home_team"]["goals"] if goal["goal_type"] == "penalty"
    )
    assert penalty_goal == {
        "player_name": "Lucas Contreras",
        "goal_type": "penalty",
        "minute": 18,
    }
    assert match.cards.filter(player_name="Elías Figueroa").exists()


def test_rebuilds_legacy_demo_match_without_substitution_events():
    call_command("seed_demo_match", stdout=StringIO())
    legacy_match = find_demo_match()
    assert legacy_match is not None
    legacy_match.substitutions.all().delete()

    call_command("seed_demo_match", stdout=StringIO())

    rebuilt_match = find_demo_match()
    assert rebuilt_match is not None
    assert rebuilt_match.id != legacy_match.id
    assert rebuilt_match.substitutions.count() == 2
    assert rebuilt_match.squad_players.filter(role="substitute").count() == 10
