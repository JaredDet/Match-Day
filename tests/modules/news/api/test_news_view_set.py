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


def test_lists_news():
    team = Team.objects.create(name="Atlético Bahía")

    older = News.objects.create(
        team=team,
        title="Noticia antigua",
        content={"blocks": [{"type": "paragraph", "text": "Contenido antiguo"}]},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 5, 18, tzinfo=UTC),
    )
    newer = News.objects.create(
        team=team,
        title="Noticia reciente",
        content={"blocks": [{"type": "paragraph", "text": "Contenido reciente"}]},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 20, 18, tzinfo=UTC),
    )

    response = APIClient().get(reverse("news-list"))

    assert response.status_code == 200
    assert [news["id"] for news in response.data] == [
        str(newer.id),
        str(older.id),
    ]

    assert response.data[0] == {
        "id": str(newer.id),
        "title": "Noticia reciente",
        "team_id": str(team.id),
        "cover_image": None,
        "content": {
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Contenido reciente",
                }
            ]
        },
        "status": "PUBLISHED",
        "scheduled_at": None,
        "published_at": "2026-08-20T18:00:00Z",
    }


def test_gets_news():
    team = Team.objects.create(name="Atlético Bahía")
    published_at = datetime(2026, 8, 20, 18, tzinfo=UTC)

    news = News.objects.create(
        team=team,
        title="Noticia completa",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Contenido de la noticia",
                }
            ]
        },
        status=NewsStatus.PUBLISHED,
        published_at=published_at,
    )

    response = APIClient().get(
        reverse("news-detail", args=[str(news.id)]),
    )

    assert response.status_code == 200
    assert response.data == {
        "id": str(news.id),
        "title": "Noticia completa",
        "team_id": str(team.id),
        "cover_image": None,
        "content": {
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Contenido de la noticia",
                }
            ]
        },
        "status": "PUBLISHED",
        "scheduled_at": None,
        "published_at": "2026-08-20T18:00:00Z",
    }


def test_returns_not_found_when_getting_unknown_news():
    response = APIClient().get(
        reverse("news-detail", args=[str(UUID(int=0))]),
    )

    assert response.status_code == 404
    assert response.data["code"] == "news_not_found"


def test_filters_news_by_status():
    published = News.objects.create(
        title="Noticia publicada",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 20, 18, tzinfo=UTC),
    )
    News.objects.create(
        title="Noticia programada",
        content={"blocks": []},
        status=NewsStatus.SCHEDULED,
        scheduled_at=datetime(2026, 9, 20, 18, tzinfo=UTC),
    )
    News.objects.create(
        title="Noticia en borrador",
        content={"blocks": []},
        status=NewsStatus.DRAFT,
    )

    response = APIClient().get(
        reverse("news-list"),
        {"status": "PUBLISHED"},
    )

    assert response.status_code == 200
    assert [news["id"] for news in response.data] == [str(published.id)]
    assert response.data[0]["status"] == "PUBLISHED"


def test_filters_news_by_team():
    atletico = Team.objects.create(name="Atlético Bahía")
    cordillera = Team.objects.create(name="Deportivo Cordillera")

    atletico_news = News.objects.create(
        team=atletico,
        title="Noticias de Atlético",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 20, 18, tzinfo=UTC),
    )
    News.objects.create(
        team=cordillera,
        title="Noticias de Cordillera",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 21, 18, tzinfo=UTC),
    )

    response = APIClient().get(
        reverse("news-list"),
        {"team_id": str(atletico.id)},
    )

    assert response.status_code == 200
    assert [news["id"] for news in response.data] == [str(atletico_news.id)]


def test_filters_news_by_published_date_range():
    News.objects.create(
        title="Antes del rango",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 1, 18, tzinfo=UTC),
    )
    inside = News.objects.create(
        title="Dentro del rango",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 15, 18, tzinfo=UTC),
    )
    News.objects.create(
        title="Después del rango",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 9, 1, 18, tzinfo=UTC),
    )

    response = APIClient().get(
        reverse("news-list"),
        {
            "published_from": "2026-08-10T00:00:00Z",
            "published_to": "2026-08-20T23:59:00Z",
        },
    )

    assert response.status_code == 200
    assert [news["id"] for news in response.data] == [str(inside.id)]


def test_rejects_news_list_with_invalid_status():
    response = APIClient().get(
        reverse("news-list"),
        {"status": "INVALID"},
    )

    assert response.status_code == 400
