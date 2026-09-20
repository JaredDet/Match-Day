from datetime import UTC, datetime
from io import StringIO

import pytest
from django.core.management import call_command

from modules.matches.domain.match import Match
from modules.news.domain.news import News, NewsStatus
from modules.news.management.commands.seed_demo_news import HOME_TEAM_NAME
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_news_seed_is_idempotent_and_does_not_change_existing_teams_players_or_matches():
    home = Team.objects.create(name=HOME_TEAM_NAME, head_coach_name="Entrenador existente")
    away = Team.objects.create(name="Rival existente")
    player = Player.objects.create(team=home, name="Jugador existente")
    match = Match.schedule(
        home_team=home, away_team=away, scheduled_at=datetime(2026, 9, 1, tzinfo=UTC)
    )
    match.save()
    original_match = Match.objects.values().get(pk=match.pk)

    call_command("seed_demo_news", stdout=StringIO())
    first_ids = set(News.objects.values_list("id", flat=True))
    call_command("seed_demo_news", stdout=StringIO())

    home.refresh_from_db()

    assert home.name == HOME_TEAM_NAME
    assert home.head_coach_name == "Entrenador existente"
    assert set(Player.objects.values_list("id", flat=True)) == {player.id}
    assert list(Match.objects.values()) == [original_match]
    assert set(News.objects.values_list("id", flat=True)) == first_ids
    assert len(first_ids) == 7
    assert News.objects.filter(status=NewsStatus.PUBLISHED).count() == 3
    assert News.objects.filter(status=NewsStatus.SCHEDULED).count() == 2
    assert News.objects.filter(status=NewsStatus.DRAFT).count() == 2
    assert News.objects.filter(team=home).count() == 2


def test_news_seed_runs_without_match_demo():
    call_command("seed_demo_news", stdout=StringIO())

    assert News.objects.count() == 7
    assert Team.objects.count() == 4
    assert not Match.objects.exists()
    assert not Player.objects.exists()
