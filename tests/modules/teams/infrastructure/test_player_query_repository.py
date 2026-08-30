import pytest
from django.utils import timezone

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
