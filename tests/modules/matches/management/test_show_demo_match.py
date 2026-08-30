from io import StringIO

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_shows_list_and_detail_for_demo_match():
    call_command("seed_demo_match", stdout=StringIO())
    output = StringIO()

    call_command("show_demo_match", stdout=output)

    result = output.getvalue()
    assert "LIST MATCHES" in result
    assert "GET MATCH" in result
    assert '"status":"finished"' in result
    assert '"formation":"4-3-3"' in result
    assert '"formation":"4-4-2"' in result
    assert '"lineup"' in result
    assert '"events"' in result
    assert "Atlético del Puerto" in result
    assert "Mateo Rojas" in result
    assert "Franco Bustos" in result
    assert result.index('"team_side":"home"') < result.index('"team_side":"away"')
