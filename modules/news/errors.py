from core.exceptions import AppException, ErrorType


class NewsErrors:
    NotFound = AppException(
        "news_not_found",
        "Noticia no encontrada",
        ErrorType.NOT_FOUND,
    )
    InvalidTitle = AppException(
        "invalid_news_title",
        "El título de la noticia es obligatorio",
        ErrorType.VALIDATION,
    )

    CannotSchedule = AppException(
        "cannot_schedule_news",
        "La noticia no puede ser programada en su estado actual",
        ErrorType.VALIDATION,
    )

    NotScheduled = AppException(
        "news_not_scheduled",
        "La noticia no está programada",
        ErrorType.VALIDATION,
    )

    AlreadyPublished = AppException(
        "news_already_published",
        "La noticia ya fue publicada",
        ErrorType.VALIDATION,
    )
