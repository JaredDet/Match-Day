from datetime import date

from modules.matches.api.contracts.requests.list_matches_request import ListMatchesRequest
from modules.matches.domain.match import MatchStatus


def test_parses_optional_list_filters():
    request = ListMatchesRequest(data={"status": "live", "date": "2026-08-30"})

    assert request.is_valid(), request.errors
    assert request.validated_data == {
        "status": MatchStatus.LIVE,
        "date": date(2026, 8, 30),
    }


def test_accepts_request_without_filters():
    request = ListMatchesRequest(data={})

    assert request.is_valid(), request.errors
    assert request.validated_data == {}


def test_rejects_invalid_list_filters():
    request = ListMatchesRequest(data={"status": "paused", "date": "30/08/2026"})

    assert not request.is_valid()
    assert set(request.errors) == {"status", "date"}
