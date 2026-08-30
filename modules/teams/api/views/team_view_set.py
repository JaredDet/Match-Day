from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.teams.api.contracts.requests.create_team_request import CreateTeamRequest
from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase


class TeamViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="teams_create",
        request=CreateTeamRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTeamResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    def create(self, request):
        request_contract = CreateTeamRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateTeamUseCase)
        team_id = use_case.execute(**request_contract.validated_data)
        return Response({"id": str(team_id)}, status=status.HTTP_201_CREATED)
