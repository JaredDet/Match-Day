from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER
from core.exceptions import AppException, ErrorType
from modules.matches.constants import (
    MAX_MATCH_MINUTE,
    MIN_MATCH_MINUTE,
)


class MatchErrors:
    InvalidOutgoingPlayer = AppException(
        "invalid_outgoing_player",
        "El jugador que sale debe estar actualmente en cancha",
        ErrorType.VALIDATION,
    )
    InvalidSubstitutePlayer = AppException(
        "invalid_substitute_player",
        "El jugador que entra debe ser un suplente que no esté en cancha",
        ErrorType.VALIDATION,
    )
    InvalidSubstitutionPlayers = AppException(
        "invalid_substitution_players",
        "Los jugadores de la sustitución deben pertenecer al mismo equipo y partido",
        ErrorType.VALIDATION,
    )
    InvalidSquadRole = AppException(
        "invalid_match_squad_role",
        "El rol del jugador en la convocatoria no es válido",
        ErrorType.VALIDATION,
    )
    PlayerNotOnField = AppException(
        "player_not_on_field",
        "Solo un jugador que está en cancha puede recibir eventos del partido",
        ErrorType.VALIDATION,
    )
    InvalidLineupSize = AppException(
        "invalid_lineup_size",
        "La alineación debe contener exactamente once jugadores",
        ErrorType.VALIDATION,
    )
    InvalidLineupCaptain = AppException(
        "invalid_lineup_captain",
        "El capitán seleccionado debe formar parte de la alineación",
        ErrorType.VALIDATION,
    )
    DuplicateLineupPlayer = AppException(
        "duplicate_lineup_player",
        "Un jugador no puede repetirse en la alineación",
        ErrorType.VALIDATION,
    )
    DuplicateLineupShirt = AppException(
        "duplicate_lineup_shirt",
        "Un número de camiseta no puede repetirse en la alineación",
        ErrorType.VALIDATION,
    )
    InvalidShirtNumber = AppException(
        "invalid_shirt_number",
        f"El número de camiseta debe estar entre {MIN_SHIRT_NUMBER} y {MAX_SHIRT_NUMBER}",
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
        "El partido no se encuentra en un estado válido para esta operación",
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
        f"El minuto debe estar entre {MIN_MATCH_MINUTE} y {MAX_MATCH_MINUTE}",
        ErrorType.VALIDATION,
    )
    InvalidTeamSide = AppException(
        "invalid_team_side",
        "El lado del equipo no es válido",
        ErrorType.VALIDATION,
    )
    InvalidCardType = AppException(
        "invalid_card_type",
        "El tipo de tarjeta no es válido",
        ErrorType.VALIDATION,
    )
