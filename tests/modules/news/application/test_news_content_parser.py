import pytest

from modules.news.application.news_content_parser import NewsContentParser
from modules.news.errors import NewsErrors


def test_accepts_valid_content():
    content = {
        "children": [
            "Este es un párrafo normal.",
            "Este tiene <b>negrita</b>.",
            "Este tiene <i>cursiva</i>.",
            "Este tiene <b><i>ambos formatos</i></b>.",
        ]
    }

    result = NewsContentParser().parse(content)

    assert result == content


def test_accepts_multiple_paragraphs():
    content = {
        "children": [
            "Primer párrafo.",
            "Segundo párrafo.",
            "Tercer párrafo.",
        ]
    }

    assert NewsContentParser().parse(content) == content


def test_accepts_nested_tags():
    content = {
        "children": [
            "<b>Texto en <i>negrita y cursiva</i></b>.",
            "<i>Texto en <b>cursiva y negrita</b></i>.",
        ]
    }

    assert NewsContentParser().parse(content) == content


def test_rejects_content_that_is_not_a_dict():
    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse([])

    assert error.value is NewsErrors.InvalidContent


def test_rejects_missing_children():
    content = {}

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_rejects_children_that_is_not_a_list():
    content = {
        "children": "Esto no es una lista",
    }

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_rejects_paragraph_that_is_not_a_string():
    content = {
        "children": [
            "Párrafo válido.",
            {"text": "Esto no es válido"},
        ]
    }

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_rejects_unknown_tag():
    content = {
        "children": [
            "Texto <u>subrayado</u>.",
        ]
    }

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_rejects_unclosed_tag():
    content = {
        "children": [
            "Texto <b>sin cerrar.",
        ]
    }

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_rejects_mismatched_tags():
    content = {
        "children": [
            "<b>Texto <i>mal cerrado</b></i>.",
        ]
    }

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_counts_only_visible_text_towards_max_length():
    content = {
        "children": [
            f"<b>{'a' * 500}</b>",
        ]
    }

    assert NewsContentParser().parse(content) == content


def test_rejects_more_than_500_visible_characters():
    content = {
        "children": [
            "a" * 501,
        ]
    }

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_counts_text_across_all_paragraphs():
    content = {
        "children": [
            "a" * 250,
            "<b>" + "b" * 250 + "</b>",
        ]
    }

    assert NewsContentParser().parse(content) == content


def test_rejects_more_than_500_characters_across_paragraphs():
    content = {
        "children": [
            "a" * 250,
            "b" * 251,
        ]
    }

    with pytest.raises(type(NewsErrors.InvalidContent)) as error:
        NewsContentParser().parse(content)

    assert error.value is NewsErrors.InvalidContent


def test_returns_original_content():
    content = {
        "children": [
            "Texto <b>válido</b>.",
        ]
    }

    result = NewsContentParser().parse(content)

    assert result is content
