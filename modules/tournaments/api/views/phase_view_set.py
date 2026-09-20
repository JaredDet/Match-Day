from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.tournaments.api.contracts.requests.create_phase_request import CreatePhaseRequest
from modules.tournaments.api.contracts.requests.list_phases_request import ListPhasesRequest
from modules.tournaments.api.contracts.requests.set_phase_status_request import (
    SetPhaseStatusRequest,
)
from modules.tournaments.api.contracts.requests.update_phase_request import UpdatePhaseRequest
from modules.tournaments.api.contracts.responses.get_phase_response import GetPhaseResponse
from modules.tournaments.api.contracts.responses.list_phases_response import ListPhasesResponse
from modules.tournaments.application.commands.create_phase_use_case import CreatePhaseUseCase
from modules.tournaments.application.commands.delete_phase_use_case import DeletePhaseUseCase
from modules.tournaments.application.commands.set_phase_status_use_case import SetPhaseStatusUseCase
from modules.tournaments.application.commands.update_phase_use_case import UpdatePhaseUseCase
from modules.tournaments.application.queries.get_phase_query import GetPhaseQuery
from modules.tournaments.application.queries.list_phases_query import ListPhasesQuery


class PhaseViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="tournaments_phases_create",
        request=CreatePhaseRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTournamentPhaseResult", fields={"id": serializers.UUIDField()}
            )
        },
    )
    def create(self, request):
        request_contract = CreatePhaseRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreatePhaseUseCase)
        entity_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(entity_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="tournaments_phases_list",
        parameters=[ListPhasesRequest],
        responses={status.HTTP_200_OK: ListPhasesResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListPhasesRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListPhasesQuery)
        result = query.execute(**request_contract.validated_data)

        return Response(ListPhasesResponse(result, many=True).data)

    @extend_schema(
        operation_id="tournaments_phases_retrieve", responses={status.HTTP_200_OK: GetPhaseResponse}
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetPhaseQuery)
        result = query.execute(pk)

        return Response(GetPhaseResponse(result).data)

    @extend_schema(
        operation_id="tournaments_phases_set_status",
        request=SetPhaseStatusRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["put"], url_path="status")
    def set_status(self, request, pk=None):
        request_contract = SetPhaseStatusRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(SetPhaseStatusUseCase)

        use_case.execute(phase_id=pk, **request_contract.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="tournaments_phase_delete",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def destroy(self, request, pk=None):
        use_case = injector_instance.get(DeletePhaseUseCase)
        use_case.execute(phase_id=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="tournaments_phase_update",
        request=UpdatePhaseRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def partial_update(self, request, pk=None):
        contract = UpdatePhaseRequest(data=request.data)
        contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(UpdatePhaseUseCase)
        use_case.execute(phase_id=pk, **contract.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)
