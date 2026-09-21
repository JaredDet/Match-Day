from core.exceptions import AppException, ErrorType


class RecommendationErrors:
    ActivityContentMismatch = AppException(
        "recommendations.activity_content_mismatch",
        "The heartbeat content does not match the registered navigation",
        ErrorType.VALIDATION,
    )
    ActivityNotFound = AppException(
        "recommendations.activity_not_found", "Navigation activity not found", ErrorType.NOT_FOUND
    )
    InvalidActiveTime = AppException(
        "recommendations.invalid_active_time",
        "Invalid accumulated active time",
        ErrorType.VALIDATION,
    )
