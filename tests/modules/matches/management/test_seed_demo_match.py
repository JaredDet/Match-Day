from io import StringIO

import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.domain.penalty_shootout import (
    PenaltyShootoutIneligibilityReason,
    PenaltyShootoutStatus,
)
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
    assert Match.objects.count() == 15
    assert Match.objects.filter(status=MatchStatus.FINISHED).count() == 8
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
    assert match.home_team.head_coach_name == "Carlos Medina"
    assert match.home_head_coach_name == "Carlos Medina"
    assert match.away_head_coach_name == "Rafael Contreras"
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
    assert not match.goals.filter(goal_type="own_goal").exists()
    assert not match.goals.filter(assist_player__isnull=False).exists()
    assert not match.penalty_attempts.exists()
    assert not match.injuries.exists()
    assert not match.var_reviews.exists()

    own_goal_match = Match.objects.get(goals__goal_type="own_goal")
    assert own_goal_match.goals.filter(goal_type="own_goal").count() == 1
    assert own_goal_match.goals.filter(assist_player__isnull=False).count() == 1

    penalty_showcase_match = Match.objects.get(penalty_attempts__isnull=False)
    assert penalty_showcase_match.penalty_attempts.filter(outcome="saved").count() == 1
    assert penalty_showcase_match.injuries.count() == 1
    injury_substitution = penalty_showcase_match.substitutions.get(reason="injury")
    assert (
        injury_substitution.player_out.player_id == penalty_showcase_match.injuries.get().player_id
    )
    assert injury_substitution.player_out.is_on_field is False
    assert (
        penalty_showcase_match.var_reviews.filter(
            reason="penalty",
            decision="confirmed",
        ).count()
        == 1
    )

    showcase_response = APIClient().get(reverse("matches-detail", args=[penalty_showcase_match.id]))
    showcase_event_types = [event["type"] for event in showcase_response.data["events"]]
    assert "penalty_attempt" in showcase_event_types
    assert "injury" in showcase_event_types
    assert "var_review" in showcase_event_types

    shootout_match = Match.objects.get(penalty_shootout__isnull=False)
    assert shootout_match.current_period == MatchPeriod.EXTRA_TIME_SECOND_HALF
    assert shootout_match.current_minute == 120
    assert shootout_match.home_goal_count == shootout_match.away_goal_count
    assert shootout_match.penalty_shootout.status == PenaltyShootoutStatus.FINISHED
    assert shootout_match.penalty_shootout.home_score == 4
    assert shootout_match.penalty_shootout.away_score == 3
    assert shootout_match.penalty_shootout.home_kick_count == 5
    assert shootout_match.penalty_shootout.away_kick_count == 5
    assert shootout_match.penalty_shootout.kicks.count() == 10

    response = APIClient().get(reverse("matches-detail", args=[shootout_match.id]))
    assert response.status_code == 200
    assert response.data["home_team"]["penalty_score"] == 4
    assert response.data["away_team"]["penalty_score"] == 3
    assert response.data["penalty_shootout"]["starting_team_side"] == "home"
    assert response.data["penalty_shootout"]["next_team_side"] is None
    assert response.data["penalty_shootout"]["winner_team_side"] == "home"
    assert "kicks" not in response.data["penalty_shootout"]
    shootout_events = [
        event for event in response.data["events"] if event["type"] == "penalty_shootout_kick"
    ]
    assert len(shootout_events) == 10
    assert shootout_events[0]["sequence_number"] == 1
    assert shootout_events[0]["outcome"] == "scored"
    assert "minute" not in shootout_events[0]
    participant_reasons = {
        participant["ineligibility_reason"]
        for participant in response.data["penalty_shootout"]["participants"]
        if not participant["is_eligible"]
    }
    assert participant_reasons == {
        PenaltyShootoutIneligibilityReason.INJURY,
        PenaltyShootoutIneligibilityReason.OPPONENT_REDUCTION,
    }

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
    detail_response = APIClient().get(reverse("matches-detail", args=[match.id]))
    assert detail_response.data["home_team"]["head_coach_name"] == "Carlos Medina"
    assert detail_response.data["away_team"]["head_coach_name"] == "Rafael Contreras"
    own_goal_summary = next(
        item for item in list_response.data if item["id"] == str(own_goal_match.id)
    )
    own_goal = next(
        goal for goal in own_goal_summary["home_team"]["goals"] if goal["goal_type"] == "own_goal"
    )
    assert own_goal["player_name"] == "Kevin Garrido"
    assisted_goal = next(
        goal for goal in own_goal_summary["away_team"]["goals"] if "assist_player_name" in goal
    )
    assisted_goal_record = own_goal_match.goals.get(assist_player__isnull=False)
    assert assisted_goal["assist_player_name"] == assisted_goal_record.assist_player_name
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
