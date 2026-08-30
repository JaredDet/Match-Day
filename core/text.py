def normalize_whitespace(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split())
