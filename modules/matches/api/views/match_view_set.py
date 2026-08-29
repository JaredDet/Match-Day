from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.matches.api.contracts.requests.create_match_request import CreateMatchRequest
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase


class MatchViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="matches_create",
        request=CreateMatchRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateMatchResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    def create(self, request):
        request_contract = CreateMatchRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateMatchUseCase)
        match_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(match_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_start",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        use_case = injector_instance.get(StartMatchUseCase)
        use_case.execute(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
