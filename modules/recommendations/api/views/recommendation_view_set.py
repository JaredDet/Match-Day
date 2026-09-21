from django.middleware.csrf import get_token
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.recommendations.api.contracts.requests.record_active_time_request import (
    RecordActiveTimeRequest,
)
from modules.recommendations.api.contracts.responses.get_recommendations_response import (
    GetRecommendationsResponse,
)
from modules.recommendations.api.visitor_cookie import get_visitor_id
from modules.recommendations.application.commands.clear_navigation_history_use_case import (
    ClearNavigationHistoryUseCase,
)
from modules.recommendations.application.commands.record_active_time_use_case import (
    RecordActiveTimeUseCase,
)
from modules.recommendations.application.queries.get_recommendations_query import (
    GetRecommendationsQuery,
)
from modules.recommendations.constants import VISITOR_COOKIE_NAME


@method_decorator(csrf_protect, name="dispatch")
class RecommendationViewSet(ViewSet):
    @extend_schema(operation_id="recommendations_list", responses={200: GetRecommendationsResponse})
    def list(self, request):
        get_token(request)
        result = injector_instance.get(GetRecommendationsQuery).execute(
            visitor_id=get_visitor_id(request)
        )
        return Response(GetRecommendationsResponse(result).data)

    @extend_schema(
        operation_id="recommendations_heartbeat",
        request=RecordActiveTimeRequest,
        responses={204: None},
    )
    @action(detail=False, methods=["post"], url_path="activity/heartbeat")
    def heartbeat(self, request):
        contract = RecordActiveTimeRequest(data=request.data)
        contract.is_valid(raise_exception=True)
        injector_instance.get(RecordActiveTimeUseCase).execute(
            visitor_id=get_visitor_id(request), **contract.validated_data
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="recommendations_clear_history", request=None, responses={204: None}
    )
    @action(detail=False, methods=["delete"], url_path="history")
    def history(self, request):
        injector_instance.get(ClearNavigationHistoryUseCase).execute(
            visitor_id=get_visitor_id(request)
        )
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(VISITOR_COOKIE_NAME, samesite="Lax")
        return response

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        patch_cache_control(response, private=True, no_store=True)
        patch_vary_headers(response, ["Cookie"])
        return response
