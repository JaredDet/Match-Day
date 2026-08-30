import pytest
from django.db import IntegrityError

from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_rejects_repeated_player_in_match_lineup():
    match = MatchMother.create(persist_teams=True)
    match.save()
    player = Player.objects.create(team=match.home_team, name="Jugador")
    match.add_lineup_player(player=player, shirt_number=8).save()

    with pytest.raises(IntegrityError):
        match.add_lineup_player(player=player, shirt_number=10).save()


def test_rejects_repeated_shirt_number_for_same_team():
    match = MatchMother.create(persist_teams=True)
    match.save()
    first = Player.objects.create(team=match.home_team, name="Jugador uno")
    second = Player.objects.create(team=match.home_team, name="Jugador dos")
    match.add_lineup_player(player=first, shirt_number=8).save()

    with pytest.raises(IntegrityError):
        match.add_lineup_player(player=second, shirt_number=8).save()


def test_rejects_more_than_one_captain_for_same_team():
    match = MatchMother.create(persist_teams=True)
    match.save()
    first = Player.objects.create(team=match.home_team, name="Capitán uno")
    second = Player.objects.create(team=match.home_team, name="Capitán dos")
    match.add_lineup_player(player=first, shirt_number=8, is_captain=True).save()

    with pytest.raises(IntegrityError):
        match.add_lineup_player(player=second, shirt_number=10, is_captain=True).save()
