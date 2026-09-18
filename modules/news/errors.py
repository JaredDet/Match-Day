from core.exceptions import AppException, ErrorType


class NewsErrors:
    InvalidTitle = AppException(
        "invalid_news_title",
        "El título de la noticia es obligatorio",
        ErrorType.VALIDATION,
    )
    TeamNotFound = AppException(
        "team_not_found",
        "Equipo no encontrado",
        ErrorType.NOT_FOUND,
    )
