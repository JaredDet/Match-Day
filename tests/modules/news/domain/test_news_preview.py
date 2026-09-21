import pytest

from core.constants import NEWS_PREVIEW_MAX_LENGTH
from modules.news.domain.news_preview import news_preview


@pytest.mark.parametrize(
    ("children", "expected"),
    [
        ([], ""),
        (["  ", "<b></b>"], ""),
        (["", "  Primer\n párrafo  ", "Segundo párrafo"], "Primer párrafo"),
        (["<b>Hola <i>equipo</i></b> &amp; afición"], "Hola equipo & afición"),
        (["á" * NEWS_PREVIEW_MAX_LENGTH], "á" * NEWS_PREVIEW_MAX_LENGTH),
        (["á" * (NEWS_PREVIEW_MAX_LENGTH + 1)], "á" * (NEWS_PREVIEW_MAX_LENGTH - 1) + "…"),
    ],
)
def test_builds_plain_text_preview(children, expected):
    content = {"children": children.copy()}

    assert news_preview(content) == expected
    assert content == {"children": children}
