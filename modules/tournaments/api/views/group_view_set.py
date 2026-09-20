from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.tournaments.api.contracts.requests.create_group_request import CreateGroupRequest
from modules.tournaments.api.contracts.requests.list_groups_request import ListGroupsRequest
from modules.tournaments.api.contracts.requests.set_group_tie_break_request import (
    SetGroupTieBreakRequest,
)
from modules.tournaments.api.contracts.requests.update_group_request import UpdateGroupRequest
from modules.tournaments.api.contracts.responses.get_group_response import GetGroupResponse
from modules.tournaments.api.contracts.responses.list_groups_response import ListGroupsResponse
from modules.tournaments.application.commands.create_group_use_case import CreateGroupUseCase
from modules.tournaments.application.commands.delete_group_use_case import DeleteGroupUseCase
from modules.tournaments.application.commands.set_group_tie_break_use_case import (
    SetGroupTieBreakUseCase,
)
from modules.tournaments.application.commands.update_group_use_case import UpdateGroupUseCase
from modules.tournaments.application.queries.get_group_query import GetGroupQuery
from modules.tournaments.application.queries.list_groups_query import ListGroupsQuery


class GroupViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="tournaments_groups_create",
        request=CreateGroupRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTournamentGroupResult", fields={"id": serializers.UUIDField()}
            )
        },
    )
    def create(self, request):
        request_contract = CreateGroupRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateGroupUseCase)
        entity_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(entity_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="tournaments_groups_list",
        parameters=[ListGroupsRequest],
        responses={status.HTTP_200_OK: ListGroupsResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListGroupsRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListGroupsQuery)
        result = query.execute(**request_contract.validated_data)

        return Response(ListGroupsResponse(result, many=True).data)

    @extend_schema(
        operation_id="tournaments_groups_retrieve", responses={status.HTTP_200_OK: GetGroupResponse}
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetGroupQuery)
        result = query.execute(pk)

        return Response(GetGroupResponse(result).data)

    @extend_schema(
        operation_id="tournaments_group_delete",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def destroy(self, request, pk=None):
        use_case = injector_instance.get(DeleteGroupUseCase)
        use_case.execute(group_id=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="tournaments_group_update",
        request=UpdateGroupRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def partial_update(self, request, pk=None):
        contract = UpdateGroupRequest(data=request.data)
        contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(UpdateGroupUseCase)
        use_case.execute(group_id=pk, **contract.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="tournaments_group_tie_break",
        request=SetGroupTieBreakRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["put"], url_path="tie-break")
    def tie_break(self, request, pk=None):
        contract = SetGroupTieBreakRequest(data=request.data)
        contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(SetGroupTieBreakUseCase)
        use_case.execute(group_id=pk, **contract.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)
