from io import StringIO

import pytest
from django.core.management import call_command

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.match_event import MatchPeriod
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
