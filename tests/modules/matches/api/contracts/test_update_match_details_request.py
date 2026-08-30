from modules.matches.api.contracts.requests.update_match_details_request import (
    UpdateMatchDetailsRequest,
)


def test_accepts_partial_match_details():
    request = UpdateMatchDetailsRequest(data={"stadium_name": "Estadio Nacional"})

    assert request.is_valid(), request.errors
    assert request.validated_data == {"stadium_name": "Estadio Nacional"}


def test_rejects_empty_match_details():
    request = UpdateMatchDetailsRequest(data={})

    assert not request.is_valid()
    assert "non_field_errors" in request.errors
