from uuid import uuid4

import pytest

from modules.news.api.contracts.requests.create_news_request import CreateNewsRequest


def test_accepts_news_data():
    team_id = uuid4()
    content = {"blocks": [{"type": "paragraph", "text": "Contenido"}]}

    request = CreateNewsRequest(
        data={
            "title": "Nueva noticia",
            "team_id": str(team_id),
            "cover_image": None,
            "content": content,
        }
    )

    assert request.is_valid()
    assert request.validated_data == {
        "title": "Nueva noticia",
        "team_id": team_id,
        "cover_image": None,
        "content": content,
    }


def test_accepts_general_news_without_team():
    content = {"blocks": []}

    request = CreateNewsRequest(
        data={
            "title": "Noticia general",
            "content": content,
        }
    )

    assert request.is_valid()
    assert request.validated_data == {
        "title": "Noticia general",
        "team_id": None,
        "content": content,
    }


@pytest.mark.parametrize("data", [{}, {"title": ""}, {"title": " "}])
def test_rejects_missing_or_blank_news_title(data):
    request = CreateNewsRequest(
        data={
            **data,
            "content": {"blocks": []},
        }
    )

    assert not request.is_valid()
    assert "title" in request.errors


def test_rejects_missing_content():
    request = CreateNewsRequest(
        data={"title": "Nueva noticia"},
    )

    assert not request.is_valid()
    assert "content" in request.errors


def test_rejects_invalid_team_id():
    request = CreateNewsRequest(
        data={
            "title": "Nueva noticia",
            "team_id": "no-es-un-uuid",
            "content": {"blocks": []},
        }
    )

    assert not request.is_valid()
    assert "team_id" in request.errors
