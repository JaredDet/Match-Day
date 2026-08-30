from core.exceptions import AppException, ErrorType


class TeamErrors:
    AlreadyExists = AppException(
        "team_already_exists",
        "Ya existe un equipo con ese nombre",
        ErrorType.CONFLICT,
    )
    InvalidPlayerName = AppException(
        "invalid_player_name",
        "El nombre del jugador es obligatorio",
        ErrorType.VALIDATION,
    )
    PlayerAlreadyExists = AppException(
        "player_already_exists",
        "Ya existe un jugador con ese nombre en el equipo",
        ErrorType.CONFLICT,
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
