from core.text import normalize_whitespace
from modules.tournaments.errors import TournamentErrors


def normalize_name(name: str, max_length: int) -> str:
    value = normalize_whitespace(name)

    if not value or len(value) > max_length:
        raise TournamentErrors.InvalidName

    return value
