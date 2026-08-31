from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER
from core.exceptions import AppException, ErrorType


class TeamErrors:
    InvalidPlayerPosition = AppException(
        "invalid_player_position",
        "La posición preferida del jugador no es válida",
        ErrorType.VALIDATION,
    )
    InvalidPlayerShirtNumber = AppException(
        "invalid_player_shirt_number",
        f"El dorsal preferido debe estar entre {MIN_SHIRT_NUMBER} y {MAX_SHIRT_NUMBER}",
        ErrorType.VALIDATION,
    )
    PlayerShirtNumberAlreadyExists = AppException(
        "player_shirt_number_already_exists",
        "Ya existe un jugador con ese dorsal preferido en el equipo",
        ErrorType.CONFLICT,
    )
    InvalidCaptain = AppException(
        "invalid_team_captain",
        "El capitán debe pertenecer al equipo",
        ErrorType.VALIDATION,
    )
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
