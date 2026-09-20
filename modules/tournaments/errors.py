from core.exceptions import AppException, ErrorType


class TournamentErrors:
    StructureLocked = AppException(
        "tournament_structure_locked",
        "La estructura tiene partidos iniciados, está cerrada o tiene rondas dependientes",
        ErrorType.CONFLICT,
    )
    HasDependencies = AppException(
        "tournament_has_dependencies",
        "Retira primero las asociaciones e inscripciones dependientes",
        ErrorType.CONFLICT,
    )
    InvalidBracket = AppException(
        "invalid_tournament_bracket",
        "Se requieren entre 2 y 64 equipos únicos, en potencia de dos, inscritos en la temporada",
        ErrorType.VALIDATION,
    )
    BracketAlreadyExists = AppException(
        "tournament_bracket_already_exists",
        "La temporada ya tiene fases eliminatorias",
        ErrorType.CONFLICT,
    )
    UnresolvedTie = AppException(
        "tournament_unresolved_tie",
        "Resuelve el empate deportivo antes de generar los cruces",
        ErrorType.CONFLICT,
    )
    IncompletePhase = AppException(
        "tournament_incomplete_phase",
        "La fase de origen debe estar finalizada, con todos sus partidos resueltos",
        ErrorType.CONFLICT,
    )
    InvalidTieBreak = AppException(
        "invalid_tournament_tie_break",
        "El orden debe incluir exactamente una vez a todos los equipos del grupo",
        ErrorType.VALIDATION,
    )
    AdvancementConflict = AppException(
        "tournament_advancement_conflict",
        "Los resultados de origen no coinciden con los cruces ya generados",
        ErrorType.CONFLICT,
    )
    BracketNotFound = AppException(
        "tournament_bracket_not_found",
        "No hay un cuadro generado en esta temporada",
        ErrorType.NOT_FOUND,
    )
    InvalidGroupCapacity = AppException(
        "invalid_group_capacity",
        "El m?ximo por grupo debe estar entre 1 y 32767",
        ErrorType.VALIDATION,
    )
    GroupFull = AppException(
        "tournament_group_full",
        "El grupo alcanz? el m?ximo de equipos permitido",
        ErrorType.CONFLICT,
    )

    NotFound = AppException("tournament_not_found", "Torneo no encontrado", ErrorType.NOT_FOUND)
    SeasonNotFound = AppException(
        "tournament_season_not_found", "Temporada no encontrada", ErrorType.NOT_FOUND
    )
    PhaseNotFound = AppException(
        "tournament_phase_not_found", "Fase no encontrada", ErrorType.NOT_FOUND
    )
    GroupNotFound = AppException(
        "tournament_group_not_found", "Grupo no encontrado", ErrorType.NOT_FOUND
    )
    GroupEntryNotFound = AppException(
        "tournament_group_entry_not_found", "Inscripción no encontrada", ErrorType.NOT_FOUND
    )
    FixtureNotFound = AppException(
        "tournament_fixture_not_found", "Asociación de partido no encontrada", ErrorType.NOT_FOUND
    )
    AlreadyExists = AppException(
        "tournament_already_exists", "Ya existe un torneo con ese slug", ErrorType.CONFLICT
    )
    SeasonAlreadyExists = AppException(
        "tournament_season_already_exists",
        "Ya existe esa temporada en el torneo",
        ErrorType.CONFLICT,
    )
    PhaseAlreadyExists = AppException(
        "tournament_phase_already_exists",
        "Ya existe una fase en esa posición o un tercer puesto",
        ErrorType.CONFLICT,
    )
    GroupAlreadyExists = AppException(
        "tournament_group_already_exists", "Ya existe ese grupo en la fase", ErrorType.CONFLICT
    )
    GroupEntryAlreadyExists = AppException(
        "tournament_group_entry_already_exists",
        "El equipo ya tiene grupo en esta fase",
        ErrorType.CONFLICT,
    )
    FixtureAlreadyExists = AppException(
        "tournament_fixture_already_exists",
        "El partido ya está asociado o la posición está ocupada",
        ErrorType.CONFLICT,
    )
    InvalidName = AppException(
        "invalid_tournament_name",
        "El nombre es obligatorio y debe respetar la longitud máxima",
        ErrorType.VALIDATION,
    )
    InvalidSlug = AppException(
        "invalid_tournament_slug", "El slug del torneo no es válido", ErrorType.VALIDATION
    )
    InvalidMetadata = AppException(
        "invalid_tournament_metadata",
        "País y categoría son obligatorios y admiten hasta 100 caracteres",
        ErrorType.VALIDATION,
    )
    InvalidPhaseKind = AppException(
        "invalid_tournament_phase_kind", "El tipo de fase no es válido", ErrorType.VALIDATION
    )
    InvalidPhaseStatus = AppException(
        "invalid_tournament_phase_status", "El estado de fase no es válido", ErrorType.VALIDATION
    )
    InvalidPhaseConfiguration = AppException(
        "invalid_tournament_phase_configuration",
        "El orden y los cupos deben ser no negativos y debe haber al menos una jornada",
        ErrorType.VALIDATION,
    )
    InvalidGroupPhase = AppException(
        "invalid_tournament_group_phase",
        "Solo las fases de grupos admiten grupos",
        ErrorType.VALIDATION,
    )
    TeamNotRegistered = AppException(
        "tournament_team_not_registered",
        "El equipo debe estar inscrito en la temporada",
        ErrorType.VALIDATION,
    )
    InvalidFixtureGroup = AppException(
        "invalid_tournament_fixture_group",
        "El grupo debe pertenecer a la fase; las eliminatorias no admiten grupo",
        ErrorType.VALIDATION,
    )
    InvalidFixtureTeams = AppException(
        "invalid_tournament_fixture_teams",
        "Los equipos deben pertenecer al grupo o temporada",
        ErrorType.VALIDATION,
    )
    InvalidFixturePosition = AppException(
        "invalid_tournament_fixture_position",
        "La posición debe ser no negativa; el tercer puesto usa la posición 1",
        ErrorType.VALIDATION,
    )
    InvalidMatchday = AppException(
        "invalid_tournament_matchday", "Jornada fuera del rango de la fase", ErrorType.VALIDATION
    )
