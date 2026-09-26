import re

from core.constants import NEWS_CONTENT_MAX_LENGTH
from modules.news.errors import NewsErrors


class NewsContentParser:
    _TOKEN_PATTERN = re.compile(r"<[^>]*>")

    def parse(self, content: dict) -> dict:
        if not isinstance(content, dict):
            raise NewsErrors.InvalidContent

        children = content.get("children")

        if not isinstance(children, list):
            raise NewsErrors.InvalidContent

        total_length = 0

        for paragraph in children:
            if not isinstance(paragraph, str):
                raise NewsErrors.InvalidContent

            total_length += self._validate_paragraph(paragraph)

        if total_length > NEWS_CONTENT_MAX_LENGTH:
            raise NewsErrors.InvalidContent

        return content

    def _validate_paragraph(self, paragraph: str) -> int:
        heading_match = re.fullmatch(
            r"<(h[1-4])>(.*)</\1>", paragraph, flags=re.DOTALL
        )
        if re.match(r"<h[1-4]>", paragraph) and heading_match is None:
            raise NewsErrors.InvalidContent

        if heading_match is not None:
            paragraph = heading_match.group(2)

        stack: list[str] = []
        text_length = 0
        position = 0

        for match in self._TOKEN_PATTERN.finditer(paragraph):
            text_length += len(paragraph[position : match.start()])

            tag = match.group()

            if tag == "<b>":
                stack.append("b")
            elif tag == "<i>":
                stack.append("i")
            elif tag == "</b>":
                self._close_tag(stack, "b")
            elif tag == "</i>":
                self._close_tag(stack, "i")
            else:
                raise NewsErrors.InvalidContent

            position = match.end()

        text_length += len(paragraph[position:])

        if stack:
            raise NewsErrors.InvalidContent

        return text_length

    @staticmethod
    def _close_tag(stack: list[str], tag: str) -> None:
        if not stack or stack[-1] != tag:
            raise NewsErrors.InvalidContent

        stack.pop()
