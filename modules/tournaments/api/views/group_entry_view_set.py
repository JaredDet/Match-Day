from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.tournaments.api.contracts.requests.create_group_entry_request import (
    CreateGroupEntryRequest,
)
from modules.tournaments.api.contracts.requests.list_group_entries_request import (
    ListGroupEntriesRequest,
)
from modules.tournaments.api.contracts.responses.get_group_entry_response import (
    GetGroupEntryResponse,
)
from modules.tournaments.api.contracts.responses.list_group_entries_response import (
    ListGroupEntriesResponse,
)
from modules.tournaments.application.commands.create_group_entry_use_case import (
    CreateGroupEntryUseCase,
)
from modules.tournaments.application.commands.delete_group_entry_use_case import (
    DeleteGroupEntryUseCase,
)
from modules.tournaments.application.queries.get_group_entry_query import GetGroupEntryQuery
from modules.tournaments.application.queries.list_group_entries_query import ListGroupEntriesQuery


class GroupEntryViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="tournaments_group_entries_create",
        request=CreateGroupEntryRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTournamentGroupEntryResult", fields={"id": serializers.UUIDField()}
            )
        },
    )
    def create(self, request):
        request_contract = CreateGroupEntryRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateGroupEntryUseCase)
        entity_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(entity_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="tournaments_group_entries_list",
        parameters=[ListGroupEntriesRequest],
        responses={status.HTTP_200_OK: ListGroupEntriesResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListGroupEntriesRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListGroupEntriesQuery)
        result = query.execute(**request_contract.validated_data)

        return Response(ListGroupEntriesResponse(result, many=True).data)

    @extend_schema(
        operation_id="tournaments_group_entries_retrieve",
        responses={status.HTTP_200_OK: GetGroupEntryResponse},
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetGroupEntryQuery)
        result = query.execute(pk)

        return Response(GetGroupEntryResponse(result).data)

    @extend_schema(
        operation_id="tournaments_group_entry_delete",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def destroy(self, request, pk=None):
        use_case = injector_instance.get(DeleteGroupEntryUseCase)
        use_case.execute(group_entry_id=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)
