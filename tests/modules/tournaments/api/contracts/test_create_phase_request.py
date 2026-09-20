from uuid import uuid4

from modules.tournaments.api.contracts.requests.create_phase_request import CreatePhaseRequest
from modules.tournaments.domain.phase import PhaseKind


def test_request_validates_without_loading_season_and_converts_enum():
    season_id = uuid4()
    request = CreatePhaseRequest(
        data=dict(season=str(season_id), name="Grupos", kind="groups", order=1)
    )
    assert request.is_valid(), request.errors
    assert request.validated_data["season_id"] == season_id
    assert request.validated_data["kind"] is PhaseKind.GROUPS


def test_request_rejects_invalid_matchday_count():
    request = CreatePhaseRequest(
        data=dict(season=str(uuid4()), name="Grupos", kind="groups", order=1, matchdays=0)
    )
    assert not request.is_valid()
    assert "matchdays" in request.errors
