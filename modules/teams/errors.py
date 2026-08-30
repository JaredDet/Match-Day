from core.exceptions import AppException, ErrorType


class TeamErrors:
    InvalidPlayerName = AppException(
        "invalid_player_name",
        "El nombre del jugador es obligatorio",
        ErrorType.VALIDATION,
    )
    PlayerNotFound = AppException(
        "player_not_found",
        "Jugador no encontrado",
        ErrorType.NOT_FOUND,
    )
    InvalidName = AppException(
        "invalid_team_name",
        "El nombre del equipo es obligatorio",
        ErrorType.VALIDATION,
    )
    NotFound = AppException(
        "team_not_found",
        "Equipo no encontrado",
        ErrorType.NOT_FOUND,
    )
