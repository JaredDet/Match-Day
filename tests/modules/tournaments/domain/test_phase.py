from uuid import uuid4

import pytest

from core.exceptions import AppException
from modules.tournaments.domain.phase import Phase, PhaseKind, PhaseStatus


def test_phase_normalizes_name_and_changes_status_without_database():
    phase = Phase.create(
        season_id=uuid4(), name="  Fase   de grupos ", kind=PhaseKind.GROUPS, order=1
    )
    assert phase.name == "Fase de grupos"
    assert phase.status == PhaseStatus.SCHEDULED
    phase.set_status(PhaseStatus.FINISHED)
    assert phase.status == PhaseStatus.FINISHED


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"name": "  "}, "invalid_tournament_name"),
        ({"kind": "invalid"}, "invalid_tournament_phase_kind"),
        ({"status": "invalid"}, "invalid_tournament_phase_status"),
        ({"order": -1}, "invalid_tournament_phase_configuration"),
        ({"qualifying_teams": -1}, "invalid_tournament_phase_configuration"),
        ({"matchdays": 0}, "invalid_tournament_phase_configuration"),
    ],
)
def test_phase_rejects_invalid_configuration_without_serializer(overrides, code):
    data = dict(season_id=uuid4(), name="Grupos", kind=PhaseKind.GROUPS, order=1)
    with pytest.raises(AppException) as error:
        Phase.create(**(data | overrides))
    assert error.value.code == code
