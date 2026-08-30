from io import StringIO

import pytest
from django.core.management import call_command

from modules.matches.domain.match import Match, MatchStatus
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
    assert Player.objects.count() == 44
    assert Match.objects.count() == 10
    assert Match.objects.filter(status=MatchStatus.FINISHED).count() == 6
    assert Match.objects.filter(status=MatchStatus.SCHEDULED).count() == 4
    assert Match.objects.filter(id=match.id).count() == 1
    assert match.status == MatchStatus.FINISHED
    assert match.home_team_name == "Atlético del Puerto"
    assert match.home_team.name == "Atlético Bahía"
    assert match.stadium_name == "Estadio del Horizonte"
    assert match.referee_name == "Alex Rivera"
    assert match.home_goal_count == 2
    assert match.away_goal_count == 1
    assert match.lineup_players.count() == 22
    assert match.lineup_players.filter(player__name="Mateo Rojas").exists()
    assert match.lineup_players.filter(player__name="Franco Bustos").exists()
    assert not match.lineup_players.filter(player__name__startswith="Jugador ").exists()
    assert match.goals.filter(disallowed_at__isnull=True).count() == 3
    assert match.goals.filter(disallowed_at__isnull=False).count() == 1
    assert match.cards.filter(rescinded_at__isnull=True).count() == 2
    assert match.cards.filter(rescinded_at__isnull=False).count() == 1
    assert match.goals.filter(player_name="Lucas Contreras").exists()
    assert match.cards.filter(player_name="Ignacio Silva").exists()
