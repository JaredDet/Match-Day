from core.exceptions import AppException, ErrorType


class MatchErrors:
    InvalidLineupSize = AppException(
        "invalid_lineup_size",
        "La alineaciÃ³n debe contener exactamente once jugadores",
        ErrorType.VALIDATION,
    )
    InvalidLineupCaptain = AppException(
        "invalid_lineup_captain",
        "La alineaciÃ³n debe tener exactamente un capitÃ¡n",
        ErrorType.VALIDATION,
    )
    DuplicateLineupPlayer = AppException(
        "duplicate_lineup_player",
        "Un jugador no puede repetirse en la alineaciÃ³n",
        ErrorType.VALIDATION,
    )
    DuplicateLineupShirt = AppException(
        "duplicate_lineup_shirt",
        "Un nÃºmero de camiseta no puede repetirse en la alineaciÃ³n",
        ErrorType.VALIDATION,
    )
    InvalidShirtNumber = AppException(
        "invalid_shirt_number",
        "El nÃºmero de camiseta debe estar entre 1 y 99",
        ErrorType.VALIDATION,
    )
    InvalidFormation = AppException(
        "invalid_formation",
        "La formación debe describir diez jugadores de campo",
        ErrorType.VALIDATION,
    )
    InvalidPlayerTeam = AppException(
        "invalid_player_team",
        "El jugador no pertenece a ninguno de los equipos del partido",
        ErrorType.VALIDATION,
    )
    CardNotFound = AppException(
        "card_not_found",
        "Tarjeta no encontrada",
        ErrorType.NOT_FOUND,
    )
    CardAlreadyRescinded = AppException(
        "card_already_rescinded",
        "La tarjeta ya fue retirada",
        ErrorType.CONFLICT,
    )
    GoalNotFound = AppException(
        "goal_not_found",
        "Gol no encontrado",
        ErrorType.NOT_FOUND,
    )
    GoalAlreadyDisallowed = AppException(
        "goal_already_disallowed",
        "El gol ya fue anulado",
        ErrorType.CONFLICT,
    )
    AlreadyExists = AppException(
        "match_already_exists",
        "Ya existe un partido entre los mismos equipos para esa fecha",
        ErrorType.CONFLICT,
    )
    NotFound = AppException(
        "match_not_found",
        "Partido no encontrado",
        ErrorType.NOT_FOUND,
    )
    InvalidState = AppException(
        "invalid_match_state",
        "El partido no se encuentra en un estado vÃ¡lido para esta operaciÃ³n",
        ErrorType.CONFLICT,
    )
    InvalidTeams = AppException(
        "invalid_match_teams",
        "Los equipos deben ser diferentes",
        ErrorType.VALIDATION,
    )
    InvalidFinishTime = AppException(
        "invalid_finish_time",
        "El partido no puede finalizar antes de haber comenzado",
        ErrorType.VALIDATION,
    )
    InvalidMinute = AppException(
        "invalid_match_minute",
        "El minuto debe estar entre 0 y 130",
        ErrorType.VALIDATION,
    )
    InvalidTeamSide = AppException(
        "invalid_team_side",
        "El lado del equipo no es vÃ¡lido",
        ErrorType.VALIDATION,
    )
    InvalidCardType = AppException(
        "invalid_card_type",
        "El tipo de tarjeta no es vÃ¡lido",
        ErrorType.VALIDATION,
    )
