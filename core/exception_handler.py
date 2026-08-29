from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.exceptions import AppException, ErrorType


def custom_exception_handler(exc, context):
    if isinstance(exc, AppException):
        status_code = {
            ErrorType.VALIDATION: 400,
            ErrorType.CONFLICT: 409,
            ErrorType.NOT_FOUND: 404,
            ErrorType.UNAUTHORIZED: 401,
            ErrorType.FORBIDDEN: 403,
        }.get(exc.error_type, 500)

        return Response(
            {"code": exc.code, "message": exc.message},
            status=status_code,
        )

    if isinstance(exc, ValidationError):
        return Response(
            {
                "code": "validation_error",
                "message": "Los datos enviados no son válidos",
                "details": exc.detail,
            },
            status=400,
        )

    return exception_handler(exc, context)
