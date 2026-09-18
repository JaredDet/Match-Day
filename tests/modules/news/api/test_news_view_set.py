from datetime import UTC, datetime
from uuid import UUID

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from modules.news.domain.news import News, NewsStatus
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_creates_news_through_injected_use_case():
    team = Team.objects.create(name="Colo-Colo")

    response = APIClient().post(
        reverse("news-list"),
        {
            "title": "  Nueva   noticia  ",
            "team_id": str(team.id),
            "content": {
                "blocks": [
                    {
                        "type": "paragraph",
                        "text": "Contenido de la noticia",
                    }
                ]
            },
        },
        format="json",
    )

    assert response.status_code == 201
    news = News.objects.get(id=UUID(response.data["id"]))

    assert news.team == team
    assert news.title == "Nueva noticia"
    assert news.content == {
        "blocks": [
            {
                "type": "paragraph",
                "text": "Contenido de la noticia",
            }
        ]
    }
    assert news.status == NewsStatus.DRAFT


def test_creates_general_news_without_team():
    response = APIClient().post(
        reverse("news-list"),
        {
            "title": "Noticia general",
            "content": {"blocks": []},
        },
        format="json",
    )

    assert response.status_code == 201
    news = News.objects.get(id=UUID(response.data["id"]))

    assert news.team is None
    assert news.status == NewsStatus.DRAFT


def test_rejects_news_with_unknown_team():
    response = APIClient().post(
        reverse("news-list"),
        {
            "title": "Nueva noticia",
            "team_id": str(UUID(int=0)),
            "content": {"blocks": []},
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["code"] == "team_not_found"


def test_publishes_news():
    news = News.objects.create(
        title="Noticia",
        content={"blocks": []},
    )

    response = APIClient().post(reverse("news-publish", args=[str(news.id)]))

    assert response.status_code == 204

    news.refresh_from_db()

    assert news.status == NewsStatus.PUBLISHED
    assert news.published_at is not None
    assert news.scheduled_at is None


def test_returns_not_found_when_publishing_unknown_news():
    response = APIClient().post(reverse("news-publish", args=[str(UUID(int=0))]))

    assert response.status_code == 404
    assert response.data["code"] == "news_not_found"


def test_unschedules_news():
    news = News.objects.create(
        title="Noticia",
        content={"blocks": []},
        status=NewsStatus.SCHEDULED,
        scheduled_at=datetime(2026, 9, 20, 15, 0, tzinfo=UTC),
    )

    response = APIClient().post(reverse("news-unschedule", args=[str(news.id)]))

    assert response.status_code == 204

    news.refresh_from_db()

    assert news.status == NewsStatus.DRAFT
    assert news.scheduled_at is None


def test_returns_not_found_when_unscheduling_unknown_news():
    response = APIClient().post(reverse("news-unschedule", args=[str(UUID(int=0))]))

    assert response.status_code == 404
    assert response.data["code"] == "news_not_found"


def test_updates_news():
    news = News.objects.create(
        title="Título anterior",
        content={"blocks": []},
    )

    response = APIClient().patch(
        reverse("news-detail", args=[str(news.id)]),
        {
            "title": "  Título   nuevo  ",
            "content": {
                "blocks": [
                    {
                        "type": "paragraph",
                        "text": "Contenido nuevo",
                    }
                ]
            },
            "cover_image": None,
        },
        format="json",
    )

    assert response.status_code == 204

    news.refresh_from_db()

    assert news.title == "Título nuevo"
    assert news.content == {
        "blocks": [
            {
                "type": "paragraph",
                "text": "Contenido nuevo",
            }
        ]
    }
    assert not news.cover_image
    assert news.status == NewsStatus.DRAFT


def test_returns_not_found_when_updating_unknown_news():
    response = APIClient().patch(
        reverse("news-detail", args=[str(UUID(int=0))]),
        {
            "title": "Título nuevo",
            "content": {"blocks": []},
            "cover_image": None,
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["code"] == "news_not_found"


def test_schedules_news():
    news = News.objects.create(
        title="Noticia",
        content={"blocks": []},
    )
    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)

    response = APIClient().post(
        reverse("news-schedule", args=[str(news.id)]),
        {
            "scheduled_at": scheduled_at.isoformat(),
        },
        format="json",
    )

    assert response.status_code == 204

    news.refresh_from_db()

    assert news.status == NewsStatus.SCHEDULED
    assert news.scheduled_at == scheduled_at


def test_returns_not_found_when_scheduling_unknown_news():
    scheduled_at = datetime(2026, 9, 20, 15, 0, tzinfo=UTC)

    response = APIClient().post(
        reverse("news-schedule", args=[str(UUID(int=0))]),
        {
            "scheduled_at": scheduled_at.isoformat(),
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["code"] == "news_not_found"


def test_deletes_news():
    news = News.objects.create(
        title="Noticia",
        content={"blocks": []},
    )

    response = APIClient().delete(
        reverse("news-detail", args=[str(news.id)]),
    )

    assert response.status_code == 204
    assert not News.objects.filter(id=news.id).exists()


def test_returns_not_found_when_deleting_unknown_news():
    response = APIClient().delete(
        reverse("news-detail", args=[str(UUID(int=0))]),
    )

    assert response.status_code == 404
    assert response.data["code"] == "news_not_found"
