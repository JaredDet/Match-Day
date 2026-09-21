import logging
from uuid import UUID

from django.middleware.csrf import get_token
from django.utils.cache import patch_cache_control, patch_vary_headers

from core.dependency_injector import injector_instance
from modules.recommendations.api.visitor_cookie import get_visitor_id, set_visitor_cookie
from modules.recommendations.application.commands.record_navigation_use_case import (
    RecordNavigationUseCase,
)
from modules.recommendations.domain.content_reference import ContentKind, ContentReference

logger = logging.getLogger(__name__)
DETAIL_ROUTES = {
    "teams-detail": ContentKind.TEAM,
    "players-detail": ContentKind.PLAYER,
    "news-detail": ContentKind.NEWS,
    "matches-detail": ContentKind.MATCH,
    "tournaments-detail": ContentKind.TOURNAMENT,
}


class NavigationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        route = request.resolver_match
        kind = DETAIL_ROUTES.get(route.url_name) if route else None
        if kind is None or request.method != "GET":
            return response
        patch_vary_headers(response, ["Cookie", "X-Navigation-Id", "X-Navigation-Intent"])
        if request.headers.get("X-Navigation-Intent") != "detail-view":
            return response
        patch_cache_control(response, private=True, no_store=True)
        if response.status_code != 200 or any(
            "prefetch" in request.headers.get(header, "").lower()
            for header in ("Purpose", "Sec-Purpose", "X-Moz")
        ):
            return response
        try:
            navigation_id = UUID(request.headers.get("X-Navigation-Id", ""))
        except ValueError:
            return response
        try:
            visitor_id = injector_instance.get(RecordNavigationUseCase).execute(
                visitor_id=get_visitor_id(request),
                navigation_id=navigation_id,
                reference=ContentReference(kind, UUID(str(response.data["id"]))),
            )
            if visitor_id is not None:
                set_visitor_cookie(request, response, visitor_id)
                get_token(request)
        except Exception:
            # Optional telemetry must not turn a successful content GET into a failure.
            logger.exception("Navigation activity could not be recorded")
        return response
