from datetime import UTC, datetime

import pytest

from modules.news.domain.news import News, NewsStatus
from modules.news.infrastructure.query_repository.news_query_repository import (
    NewsQueryRepository,
)
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def test_lists_news_ordered_by_published_at():
    team = Team.objects.create(name="Atlético Bahía")

    older = News.objects.create(
        team=team,
        title="Noticia antigua",
        content={"blocks": ["antigua"]},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 5, 18, tzinfo=UTC),
    )
    newer = News.objects.create(
        team=team,
        title="Noticia reciente",
        content={"blocks": ["reciente"]},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 20, 18, tzinfo=UTC),
    )

    result = NewsQueryRepository().list()

    assert [news.id for news in result] == [newer.id, older.id]
    assert [news.title for news in result] == [
        "Noticia reciente",
        "Noticia antigua",
    ]


def test_returns_all_news_fields():
    team = Team.objects.create(name="Atlético Bahía")
    published_at = datetime(2026, 8, 20, 18, tzinfo=UTC)

    news = News.objects.create(
        team=team,
        title="Noticia completa",
        content={"blocks": [{"type": "paragraph", "text": "Contenido"}]},
        status=NewsStatus.PUBLISHED,
        published_at=published_at,
    )

    result = NewsQueryRepository().list()

    assert len(result) == 1
    item = result[0]

    assert item.id == news.id
    assert item.title == "Noticia completa"
    assert item.team_id == team.id
    assert item.cover_image is None
    assert item.content == {"blocks": [{"type": "paragraph", "text": "Contenido"}]}
    assert item.status == NewsStatus.PUBLISHED
    assert item.scheduled_at is None
    assert item.published_at == published_at


def test_gets_all_news_fields():
    team = Team.objects.create(name="Atlético Bahía")
    published_at = datetime(2026, 8, 20, 18, tzinfo=UTC)

    news = News.objects.create(
        team=team,
        title="Noticia completa",
        content={"blocks": [{"type": "paragraph", "text": "Contenido"}]},
        status=NewsStatus.PUBLISHED,
        published_at=published_at,
    )

    result = NewsQueryRepository().get(news.id)

    assert result.id == news.id
    assert result.title == "Noticia completa"
    assert result.team_id == team.id
    assert result.cover_image is None
    assert result.content == {"blocks": [{"type": "paragraph", "text": "Contenido"}]}
    assert result.status == NewsStatus.PUBLISHED
    assert result.scheduled_at is None
    assert result.published_at == published_at


def test_returns_none_when_getting_unknown_news():
    assert NewsQueryRepository().get(News().id) is None


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

    result = NewsQueryRepository().list(status=NewsStatus.PUBLISHED)

    assert [news.id for news in result] == [published.id]
    assert result[0].status == NewsStatus.PUBLISHED


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

    result = NewsQueryRepository().list(team_id=atletico.id)

    assert [news.id for news in result] == [atletico_news.id]
    assert result[0].team_id == atletico.id


def test_filters_news_by_published_date_range():
    before = News.objects.create(
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
    after = News.objects.create(
        title="Después del rango",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 9, 1, 18, tzinfo=UTC),
    )

    result = NewsQueryRepository().list(
        published_from=datetime(2026, 8, 10, 0, tzinfo=UTC),
        published_to=datetime(2026, 8, 20, 23, 59, tzinfo=UTC),
    )

    assert [news.id for news in result] == [inside.id]
    assert before.id not in [news.id for news in result]
    assert after.id not in [news.id for news in result]


def test_filters_news_from_published_date():
    older = News.objects.create(
        title="Noticia antigua",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 1, 18, tzinfo=UTC),
    )
    newer = News.objects.create(
        title="Noticia reciente",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 20, 18, tzinfo=UTC),
    )

    result = NewsQueryRepository().list(
        published_from=datetime(2026, 8, 10, 0, tzinfo=UTC),
    )

    assert [news.id for news in result] == [newer.id]
    assert older.id not in [news.id for news in result]


def test_filters_news_until_published_date():
    older = News.objects.create(
        title="Noticia antigua",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 1, 18, tzinfo=UTC),
    )
    newer = News.objects.create(
        title="Noticia reciente",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 20, 18, tzinfo=UTC),
    )

    result = NewsQueryRepository().list(
        published_to=datetime(2026, 8, 10, 0, tzinfo=UTC),
    )

    assert [news.id for news in result] == [older.id]
    assert newer.id not in [news.id for news in result]


def test_combines_status_team_and_published_date_filters():
    atletico = Team.objects.create(name="Atlético Bahía")
    cordillera = Team.objects.create(name="Deportivo Cordillera")

    matching = News.objects.create(
        team=atletico,
        title="Noticia que coincide",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 15, 18, tzinfo=UTC),
    )

    News.objects.create(
        team=atletico,
        title="Estado incorrecto",
        content={"blocks": []},
        status=NewsStatus.DRAFT,
    )

    News.objects.create(
        team=cordillera,
        title="Equipo incorrecto",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 15, 18, tzinfo=UTC),
    )

    News.objects.create(
        team=atletico,
        title="Fecha incorrecta",
        content={"blocks": []},
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 9, 15, 18, tzinfo=UTC),
    )

    result = NewsQueryRepository().list(
        status=NewsStatus.PUBLISHED,
        team_id=atletico.id,
        published_from=datetime(2026, 8, 1, tzinfo=UTC),
        published_to=datetime(2026, 8, 31, 23, 59, tzinfo=UTC),
    )

    assert [news.id for news in result] == [matching.id]
