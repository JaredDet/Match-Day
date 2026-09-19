from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

from modules.news.management.commands.publish_scheduled_news import (
    ACTIVE_INTERVAL_SECONDS,
    DAILY_INTERVAL_SECONDS,
    Command,
)


def create_scheduled_news(scheduled_at):
    news = Mock()
    news.scheduled_at = scheduled_at
    return news


def test_get_next_interval_returns_daily_interval_when_there_are_no_scheduled_news():
    repository = Mock()
    repository.get_next_scheduled.return_value = None

    result = Command._get_next_interval(repository)

    assert result == DAILY_INTERVAL_SECONDS


def test_get_next_interval_returns_daily_interval_when_next_news_is_more_than_24_hours_away():
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    repository = Mock()
    repository.get_next_scheduled.return_value = create_scheduled_news(
        now + timedelta(hours=24, minutes=1)
    )

    with patch(
        "modules.news.management.commands.publish_scheduled_news.timezone.now",
        return_value=now,
    ):
        result = Command._get_next_interval(repository)

    assert result == DAILY_INTERVAL_SECONDS


def test_get_next_interval_returns_active_interval_when_next_news_is_24_hours_away():
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    repository = Mock()
    repository.get_next_scheduled.return_value = create_scheduled_news(now + timedelta(hours=24))

    with patch(
        "modules.news.management.commands.publish_scheduled_news.timezone.now",
        return_value=now,
    ):
        result = Command._get_next_interval(repository)

    assert result == ACTIVE_INTERVAL_SECONDS


def test_get_next_interval_returns_active_interval_when_next_news_is_less_than_24_hours_away():
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    repository = Mock()
    repository.get_next_scheduled.return_value = create_scheduled_news(now + timedelta(hours=5))

    with patch(
        "modules.news.management.commands.publish_scheduled_news.timezone.now",
        return_value=now,
    ):
        result = Command._get_next_interval(repository)

    assert result == ACTIVE_INTERVAL_SECONDS


def test_get_next_interval_returns_active_interval_when_news_is_already_due():
    now = datetime(2026, 9, 18, 15, 0, tzinfo=UTC)

    repository = Mock()
    repository.get_next_scheduled.return_value = create_scheduled_news(now - timedelta(minutes=5))

    with patch(
        "modules.news.management.commands.publish_scheduled_news.timezone.now",
        return_value=now,
    ):
        result = Command._get_next_interval(repository)

    assert result == ACTIVE_INTERVAL_SECONDS


def test_handle_once_publishes_scheduled_news():
    command = Command()

    publish_use_case = Mock()
    publish_use_case.execute.return_value = 2

    news_repository = Mock()
    news_repository.get_next_scheduled.return_value = None

    with patch(
        "modules.news.management.commands.publish_scheduled_news.injector_instance.get",
        side_effect=[publish_use_case, news_repository],
    ):
        command.handle(once=True)

    publish_use_case.execute.assert_called_once()


def test_handle_once_does_not_sleep():
    command = Command()

    publish_use_case = Mock()
    publish_use_case.execute.return_value = 0

    news_repository = Mock()
    news_repository.get_next_scheduled.return_value = None

    with (
        patch(
            "modules.news.management.commands.publish_scheduled_news.injector_instance.get",
            side_effect=[publish_use_case, news_repository],
        ),
        patch(
            "modules.news.management.commands.publish_scheduled_news.time.sleep",
        ) as sleep,
    ):
        command.handle(once=True)

    publish_use_case.execute.assert_called_once()
    sleep.assert_not_called()


def test_handle_once_gets_next_interval_after_publishing():
    command = Command()

    publish_use_case = Mock()
    publish_use_case.execute.return_value = 1

    news_repository = Mock()

    with (
        patch(
            "modules.news.management.commands.publish_scheduled_news.injector_instance.get",
            side_effect=[publish_use_case, news_repository],
        ),
        patch.object(
            Command,
            "_get_next_interval",
            return_value=300,
        ) as get_next_interval,
    ):
        command.handle(once=True)

    publish_use_case.execute.assert_called_once()
    get_next_interval.assert_called_once_with(news_repository)


def test_handle_re_raises_exception_with_once():
    command = Command()

    publish_use_case = Mock()
    publish_use_case.execute.side_effect = RuntimeError("error")

    news_repository = Mock()

    with (
        patch(
            "modules.news.management.commands.publish_scheduled_news.injector_instance.get",
            side_effect=[publish_use_case, news_repository],
        ),
        patch(
            "modules.news.management.commands.publish_scheduled_news.logger.exception",
        ),
    ):
        try:
            command.handle(once=True)
        except RuntimeError as exception:
            assert str(exception) == "error"
        else:
            raise AssertionError("Expected RuntimeError")
