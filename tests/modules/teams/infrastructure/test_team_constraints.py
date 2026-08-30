import pytest
from django.db import IntegrityError

from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_team_name_is_unique_case_insensitively():
    Team.objects.create(name="Colo-Colo")

    with pytest.raises(IntegrityError):
        Team.objects.create(name="colo-colo")


def test_player_name_is_unique_case_insensitively_within_team():
    team = Team.objects.create(name="Colo-Colo")
    Player.objects.create(team=team, name="Jugador")

    with pytest.raises(IntegrityError):
        Player.objects.create(team=team, name="jugador")


def test_same_player_name_is_allowed_on_different_teams():
    first_team = Team.objects.create(name="Equipo A")
    second_team = Team.objects.create(name="Equipo B")

    Player.objects.create(team=first_team, name="Jugador")
    Player.objects.create(team=second_team, name="Jugador")
