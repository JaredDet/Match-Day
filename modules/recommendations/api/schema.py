from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

NAVIGATION_PARAMETERS = [
    OpenApiParameter(
        "X-Navigation-Intent",
        OpenApiTypes.STR,
        OpenApiParameter.HEADER,
        enum=["detail-view"],
        required=False,
        description="Mark an actual detail-page navigation. Omit for polling and prefetch.",
    ),
    OpenApiParameter(
        "X-Navigation-Id",
        OpenApiTypes.UUID,
        OpenApiParameter.HEADER,
        required=False,
        description="New UUID per page visit; reuse for retries and heartbeats.",
    ),
]
