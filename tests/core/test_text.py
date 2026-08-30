import pytest

from core.text import normalize_whitespace


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  Universidad   de   Chile  ", "Universidad de Chile"),
        ("Nombre", "Nombre"),
        ("   ", ""),
        ("", ""),
        (None, ""),
    ],
)
def test_normalizes_whitespace(value, expected):
    assert normalize_whitespace(value) == expected
