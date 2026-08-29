from datetime import timedelta

import pytest
from django.utils import timezone

from core.dependency_injector import injector_instance
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.domain.match import Match, MatchStatus

pytestmark = pytest.mark.django_db


def test_create_match_use_case_is_wired_to_django_repository():
    match_id = injector_instance.get(CreateMatchUseCase).execute(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now() + timedelta(hours=1),
    )

    match = Match.objects.get(id=match_id)
    assert match.status == MatchStatus.SCHEDULED
    assert match.home_team_name == "Colo-Colo"
