from io import StringIO

import pytest
from django.core.management import call_command

from modules.matches.domain.match import Match
from modules.teams.domain.team import Team
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.domain.phase import Phase, PhaseStatus
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament

pytestmark = pytest.mark.django_db


def test_tournament_seed_is_complete_and_idempotent(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    call_command("seed_demo_tournament", stdout=StringIO())
    call_command("seed_demo_tournament", stdout=StringIO())

    assert Tournament.objects.count() == 1
    assert Season.objects.count() == 1
    assert Team.objects.count() == 4
    assert Match.objects.count() == 15
    assert Phase.objects.count() == 4
    assert Group.objects.count() == 1
    assert GroupEntry.objects.count() == 4
    assert Fixture.objects.count() == 10
    assert Phase.objects.filter(status=PhaseStatus.FINISHED).count() == 2
    assert Phase.objects.filter(status=PhaseStatus.LIVE).count() == 1
    assert not Team.objects.filter(crest="").exists()
    assert Tournament.objects.exclude(logo="").exists()
