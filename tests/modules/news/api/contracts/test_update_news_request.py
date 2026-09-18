import pytest

from modules.news.api.contracts.requests.update_news_request import UpdateNewsRequest


def test_accepts_news_data():
    content = {
        "blocks": [
            {
                "type": "paragraph",
                "text": "Contenido de la noticia",
            }
        ]
    }

    request = UpdateNewsRequest(
        data={
            "title": "Noticia actualizada",
            "content": content,
            "cover_image": None,
        }
    )

    assert request.is_valid()
    assert request.validated_data == {
        "title": "Noticia actualizada",
        "content": content,
        "cover_image": None,
    }


@pytest.mark.parametrize("data", [{}, {"title": ""}, {"title": " "}])
def test_rejects_missing_or_blank_news_title(data):
    request = UpdateNewsRequest(
        data={
            **data,
            "content": {"blocks": []},
        }
    )

    assert not request.is_valid()
    assert "title" in request.errors


def test_rejects_missing_content():
    request = UpdateNewsRequest(
        data={
            "title": "Noticia actualizada",
        }
    )

    assert not request.is_valid()
    assert "content" in request.errors


def test_accepts_null_cover_image():
    request = UpdateNewsRequest(
        data={
            "title": "Noticia actualizada",
            "content": {"blocks": []},
            "cover_image": None,
        }
    )

    assert request.is_valid()
    assert request.validated_data["cover_image"] is None
