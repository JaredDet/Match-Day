from modules.news.api.contracts.requests.schedule_news_request import ScheduleNewsRequest


def test_accepts_scheduled_at():
    request = ScheduleNewsRequest(
        data={
            "scheduled_at": "2026-09-20T15:00:00Z",
        }
    )

    assert request.is_valid()
    assert request.validated_data["scheduled_at"] is not None


def test_rejects_missing_scheduled_at():
    request = ScheduleNewsRequest(data={})

    assert not request.is_valid()
    assert "scheduled_at" in request.errors


def test_rejects_invalid_scheduled_at():
    request = ScheduleNewsRequest(
        data={
            "scheduled_at": "no-es-una-fecha",
        }
    )

    assert not request.is_valid()
    assert "scheduled_at" in request.errors
