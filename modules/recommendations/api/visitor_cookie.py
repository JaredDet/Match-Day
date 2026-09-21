from uuid import UUID

from modules.recommendations.constants import (
    VISITOR_COOKIE_MAX_AGE,
    VISITOR_COOKIE_NAME,
    VISITOR_COOKIE_SALT,
)


def get_visitor_id(request):
    value = request.get_signed_cookie(
        VISITOR_COOKIE_NAME, default=None, salt=VISITOR_COOKIE_SALT, max_age=VISITOR_COOKIE_MAX_AGE
    )
    try:
        return UUID(value) if value else None
    except (ValueError, TypeError):
        return None


def set_visitor_cookie(request, response, visitor_id):
    response.set_signed_cookie(
        VISITOR_COOKIE_NAME,
        str(visitor_id),
        salt=VISITOR_COOKIE_SALT,
        max_age=VISITOR_COOKIE_MAX_AGE,
        httponly=True,
        secure=request.is_secure(),
        samesite="Lax",
    )
