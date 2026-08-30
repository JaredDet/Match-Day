from datetime import timedelta

import pytest
from django.utils import timezone

from core.dependency_injector import injector_instance
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.domain.match import Match, MatchStatus
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_create_match_use_case_is_wired_to_django_repository():
    home_team = Team.objects.create(name="Colo-Colo")
    away_team = Team.objects.create(name="Universidad de Chile")
    match_id = injector_instance.get(CreateMatchUseCase).execute(
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        scheduled_at=timezone.now() + timedelta(hours=1),
    )

    match = Match.objects.get(id=match_id)
    assert match.status == MatchStatus.SCHEDULED
    assert match.home_team == home_team
