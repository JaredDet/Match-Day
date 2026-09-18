from datetime import UTC, datetime
from uuid import uuid4

from modules.news.api.contracts.requests.list_news_request import ListNewsRequest
from modules.news.domain.news import NewsStatus


def test_accepts_optional_news_filters():
    team_id = uuid4()
    published_from = datetime(2026, 8, 1, tzinfo=UTC)
    published_to = datetime(2026, 8, 31, tzinfo=UTC)

    request = ListNewsRequest(
        data={
            "status": "PUBLISHED",
            "team_id": str(team_id),
            "published_from": published_from.isoformat(),
            "published_to": published_to.isoformat(),
        }
    )

    assert request.is_valid(), request.errors
    assert request.validated_data == {
        "status": NewsStatus.PUBLISHED,
        "team_id": team_id,
        "published_from": published_from,
        "published_to": published_to,
    }


def test_defaults_news_filters_to_none():
    request = ListNewsRequest(data={})

    assert request.is_valid(), request.errors
    assert request.validated_data == {
        "status": None,
        "team_id": None,
        "published_from": None,
        "published_to": None,
    }
