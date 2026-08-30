import pytest
from django.utils import timezone

from modules.matches.domain.card import Card, CardType
from modules.matches.domain.goal import Goal
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_lineup_player import MatchLineupPlayer
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from modules.teams.infrastructure.query_repository.player_query_repository import (
    PlayerQueryRepository,
)
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_lists_players_with_team_and_permanent_captain_status():
    team = Team.objects.create(name="Atlético Bahía")
    other_team = Team.objects.create(name="Deportivo Cordillera")
    captain = Player.objects.create(team=team, name="Mateo Rojas")
    Player.objects.create(team=team, name="Lucas Contreras")
    Player.objects.create(team=other_team, name="Franco Bustos")
    team.captain = captain
    team.save()
    match = MatchMother.create(
        home_team=team,
        away_team=other_team,
        status=MatchStatus.FINISHED,
    )
    match.save()
    MatchLineupPlayer.objects.create(
        match=match,
        player=captain,
        team_side=TeamSide.HOME,
        shirt_number=10,
        is_captain=True,
    )
    Goal.objects.create(
        match=match,
        player=captain,
        team_side=TeamSide.HOME,
        player_name=captain.name,
        minute=20,
    )
    Goal.objects.create(
        match=match,
        player=captain,
        team_side=TeamSide.HOME,
        player_name=captain.name,
        minute=30,
        disallowed_at=timezone.now(),
    )

    result = PlayerQueryRepository().list()

    assert [player.name for player in result] == [
        "Franco Bustos",
        "Lucas Contreras",
        "Mateo Rojas",
    ]
    mateo = result[-1]
    assert mateo.team.id == team.id
    assert mateo.team.name == "Atlético Bahía"
    assert mateo.is_captain is True
    assert mateo.appearances == 1
    assert mateo.goals == 1


def test_filters_players_by_team_and_unicode_case_insensitive_search():
    team = Team.objects.create(name="Atlético Bahía")
    other_team = Team.objects.create(name="Deportivo Cordillera")
    Player.objects.create(team=team, name="Óscar Méndez")
    Player.objects.create(team=other_team, name="Óscar Silva")

    result = PlayerQueryRepository().list(search="ÓSCAR", team_id=team.id)

    assert [player.name for player in result] == ["Óscar Méndez"]


def test_gets_player_statistics_and_recent_match_from_player_perspective():
    team = Team.objects.create(name="Atlético Bahía")
    opponent = Team.objects.create(name="Deportivo Cordillera")
    player = Player.objects.create(team=team, name="Mateo Rojas")
    team.captain = player
    team.save()
    match = MatchMother.create(
        home_team=team,
        away_team=opponent,
        status=MatchStatus.FINISHED,
    )
    match.home_goal_count = 2
    match.away_goal_count = 1
    match.save()
    MatchLineupPlayer.objects.create(
        match=match,
        player=player,
        team_side=TeamSide.HOME,
        shirt_number=10,
        is_captain=True,
    )
    Goal.objects.create(
        match=match,
        player=player,
        team_side=TeamSide.HOME,
        player_name=player.name,
        minute=20,
    )
    Card.objects.create(
        match=match,
        player=player,
        team_side=TeamSide.HOME,
        player_name=player.name,
        card_type=CardType.YELLOW,
        minute=35,
    )
    Card.objects.create(
        match=match,
        player=player,
        team_side=TeamSide.HOME,
        player_name=player.name,
        card_type=CardType.RED,
        minute=70,
        rescinded_at=timezone.now(),
    )

    result = PlayerQueryRepository().get(player.id)

    assert result.name == "Mateo Rojas"
    assert result.is_captain is True
    assert result.statistics.appearances == 1
    assert result.statistics.goals == 1
    assert result.statistics.yellow_cards == 1
    assert result.statistics.red_cards == 0
    assert len(result.recent_matches) == 1
    recent = result.recent_matches[0]
    assert recent.opponent.id == opponent.id
    assert recent.opponent.name == "Deportivo Cordillera"
    assert recent.result == "win"
    assert recent.goals == 1
    assert recent.yellow_cards == 1
    assert recent.red_cards == 0


def test_returns_none_when_getting_unknown_player():
    assert PlayerQueryRepository().get(Player().id) is None
