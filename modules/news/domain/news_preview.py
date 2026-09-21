import re
from html import unescape

from core.constants import NEWS_PREVIEW_MAX_LENGTH
from core.text import normalize_whitespace


def news_preview(content: dict) -> str:
    for paragraph in content.get("children", []):
        text = normalize_whitespace(unescape(re.sub(r"</?[bi]>", "", paragraph)))

        if not text:
            continue

        if len(text) <= NEWS_PREVIEW_MAX_LENGTH:
            return text

        return text[: NEWS_PREVIEW_MAX_LENGTH - 1].rstrip() + "…"

    return ""
