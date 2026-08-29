import pytest
from rest_framework.exceptions import NotFound, ValidationError

from core.exception_handler import custom_exception_handler
from core.exceptions import AppException, ErrorType


@pytest.mark.parametrize(
    ("error_type", "expected_status"),
    [
        (ErrorType.VALIDATION, 400),
        (ErrorType.UNAUTHORIZED, 401),
        (ErrorType.FORBIDDEN, 403),
        (ErrorType.NOT_FOUND, 404),
        (ErrorType.CONFLICT, 409),
        (ErrorType.UNEXPECTED, 500),
    ],
)
def test_formats_application_errors(error_type, expected_status):
    response = custom_exception_handler(
        AppException("sample_error", "Ocurrió un error", error_type),
        context={},
    )

    assert response.status_code == expected_status
    assert response.data == {
        "code": "sample_error",
        "message": "Ocurrió un error",
    }


def test_formats_serializer_validation_errors_with_the_common_error_contract():
    response = custom_exception_handler(
        ValidationError({"country": ["Debe tener exactamente 2 caracteres."]}),
        context={},
    )

    assert response.status_code == 400
    assert response.data == {
        "code": "validation_error",
        "message": "Los datos enviados no son válidos",
        "details": {"country": ["Debe tener exactamente 2 caracteres."]},
    }


def test_delegates_framework_exceptions_to_drf():
    response = custom_exception_handler(NotFound(), context={})

    assert response.status_code == 404
