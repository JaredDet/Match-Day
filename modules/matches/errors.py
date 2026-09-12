from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER
from core.exceptions import AppException, ErrorType
from modules.matches.constants import (
    MAX_MATCH_MINUTE,
    MIN_MATCH_MINUTE,
)


class MatchErrors:
    InvalidPenaltyAttemptOutcome = AppException(
        "invalid_penalty_attempt_outcome",
        "El resultado del penal no es válido",
        ErrorType.VALIDATION,
    )
    InvalidVarReviewReason = AppException(
        "invalid_var_review_reason",
        "El motivo de la revisión VAR no es válido",
        ErrorType.VALIDATION,
    )
    InvalidVarReviewDecision = AppException(
        "invalid_var_review_decision",
        "La decisión de la revisión VAR no es válida",
        ErrorType.VALIDATION,
    )
    ReviewedEventNotFound = AppException(
        "reviewed_event_not_found",
        "El evento revisado no pertenece al partido",
        ErrorType.NOT_FOUND,
    )
    InvalidExtraTimeState = AppException(
        "invalid_extra_time_state",
        "La prórroga solo puede comenzar al finalizar el segundo tiempo",
        ErrorType.CONFLICT,
    )
    ExtraTimeRequiresTie = AppException(
        "extra_time_requires_tie",
        "La prórroga solo puede comenzar con el marcador empatado",
        ErrorType.CONFLICT,
    )
    InvalidGoalType = AppException(
        "invalid_goal_type",
        "El tipo de gol no es válido",
        ErrorType.VALIDATION,
    )
    InvalidGoalAssist = AppException(
        "invalid_goal_assist",
        "La asistencia debe corresponder a otro jugador en cancha del equipo goleador",
        ErrorType.VALIDATION,
    )
    InvalidPenaltyKickOutcome = AppException(
        "invalid_penalty_kick_outcome",
        "El resultado del lanzamiento no es válido",
        ErrorType.VALIDATION,
    )
    InvalidPenaltyShootoutPlayer = AppException(
        "invalid_penalty_shootout_player",
        "El lanzador debe seguir habilitado y en cancha",
        ErrorType.VALIDATION,
    )
    InvalidPenaltyShootoutState = AppException(
        "invalid_penalty_shootout_state",
        "La tanda solo puede comenzar al finalizar el tiempo de juego",
        ErrorType.CONFLICT,
    )
    PenaltyShootoutRequiresTie = AppException(
        "penalty_shootout_requires_tie",
        "La tanda solo puede comenzar con el marcador empatado",
        ErrorType.CONFLICT,
    )
    PenaltyShootoutNotFound = AppException(
        "penalty_shootout_not_found",
        "Tanda de penales no encontrada",
        ErrorType.NOT_FOUND,
    )
    PenaltyShootoutAlreadyExists = AppException(
        "penalty_shootout_already_exists",
        "El partido ya tiene una tanda de penales",
        ErrorType.CONFLICT,
    )
    PenaltyShootoutAlreadyFinished = AppException(
        "penalty_shootout_already_finished",
        "La tanda de penales ya finalizó",
        ErrorType.CONFLICT,
    )
    PenaltyShootoutAlreadyDecided = AppException(
        "penalty_shootout_already_decided",
        "La tanda ya tiene un ganador y no admite más lanzamientos",
        ErrorType.CONFLICT,
    )
    PenaltyShootoutNotDecided = AppException(
        "penalty_shootout_not_decided",
        "La tanda todavía no tiene un ganador",
        ErrorType.CONFLICT,
    )
    InvalidPenaltyShootoutTurn = AppException(
        "invalid_penalty_shootout_turn",
        "El lanzamiento no corresponde al equipo esperado",
        ErrorType.CONFLICT,
    )
    PenaltyShootoutKickerAlreadyUsed = AppException(
        "penalty_shootout_kicker_already_used",
        "El lanzador no puede repetir hasta que todos los jugadores habilitados hayan lanzado",
        ErrorType.CONFLICT,
    )
    InvalidPenaltyShootoutExclusions = AppException(
        "invalid_penalty_shootout_exclusions",
        "Debe excluirse exactamente la diferencia de jugadores del equipo con más habilitados",
        ErrorType.VALIDATION,
    )
    InvalidPenaltyShootoutDepartureReason = AppException(
        "invalid_penalty_shootout_departure_reason",
        "El motivo de salida durante la tanda no es válido",
        ErrorType.VALIDATION,
    )
    InvalidPenaltyShootoutReduction = AppException(
        "invalid_penalty_shootout_reduction",
        "La reducción debe retirar un jugador habilitado de cada equipo",
        ErrorType.VALIDATION,
    )
    UnequalPenaltyShootoutParticipants = AppException(
        "unequal_penalty_shootout_participants",
        "La tanda no puede continuar con distinta cantidad de jugadores habilitados",
        ErrorType.CONFLICT,
    )
    InvalidSentOffReason = AppException(
        "invalid_sent_off_reason",
        "El motivo de expulsión no es válido",
        ErrorType.VALIDATION,
    )
    PlayerSentOff = AppException(
        "player_sent_off",
        "Un jugador expulsado no puede participar nuevamente en el partido",
        ErrorType.CONFLICT,
    )
    MissingFormation = AppException(
        "missing_match_formation",
        "Ambos equipos deben tener una formación antes de iniciar el partido",
        ErrorType.CONFLICT,
    )
    InvalidStartingSquad = AppException(
        "invalid_starting_squad",
        "Cada equipo debe comenzar con exactamente once titulares en cancha",
        ErrorType.CONFLICT,
    )
    ClockCannotGoBackwards = AppException(
        "match_clock_cannot_go_backwards",
        "El reloj del partido no puede retroceder dentro del mismo periodo",
        ErrorType.CONFLICT,
    )
    EventAheadOfClock = AppException(
        "event_ahead_of_match_clock",
        "El evento no puede ocurrir después del minuto actual del partido",
        ErrorType.VALIDATION,
    )
    PeriodMismatch = AppException(
        "match_period_mismatch",
        "El partido no se encuentra en el periodo indicado",
        ErrorType.CONFLICT,
    )
    InvalidPeriod = AppException(
        "invalid_match_period",
        "El partido no se encuentra en un periodo válido para registrar eventos",
        ErrorType.CONFLICT,
    )
    InvalidAddedMinute = AppException(
        "invalid_added_minute",
        "El tiempo añadido solo puede aplicarse al final de cada tiempo",
        ErrorType.VALIDATION,
    )
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
    InvalidSubstitutionReason = AppException(
        "invalid_substitution_reason",
        "El motivo de la sustitución no es válido",
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
