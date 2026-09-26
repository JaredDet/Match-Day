import re
from html import unescape

from core.constants import NEWS_PREVIEW_MAX_LENGTH
from core.text import normalize_whitespace


def news_preview(content: dict, custom_preview: str = "") -> str:
    source = custom_preview.strip()
    if not source:
        source = next(
            (
                block
                for block in content.get("children", [])
                if not re.match(r"<h[1-4]>", block)
                and normalize_whitespace(unescape(re.sub(r"<[^>]*>", "", block)))
            ),
            "",
        )
    text = normalize_whitespace(unescape(re.sub(r"<[^>]*>", "", source)))
    if len(text) <= NEWS_PREVIEW_MAX_LENGTH:
        return text
    return text[: NEWS_PREVIEW_MAX_LENGTH - 1].rstrip() + "…"
