from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.news.api.contracts.requests.create_news_request import CreateNewsRequest
from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.application.commands.publish_news_use_case import PublishNewsUseCase
from modules.news.application.commands.unschedule_news_use_case import UnscheduleNewsUseCase


class NewsViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="news_create",
        request=CreateNewsRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateNewsResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    def create(self, request):
        request_contract = CreateNewsRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateNewsUseCase)
        news_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(news_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="news_publish",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        use_case = injector_instance.get(PublishNewsUseCase)
        use_case.execute(news_id=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="news_unschedule",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="unschedule")
    def unschedule(self, request, pk=None):
        use_case = injector_instance.get(UnscheduleNewsUseCase)
        use_case.execute(news_id=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)
