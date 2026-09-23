from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient


@override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:3000"])
def test_allows_frontend_preflight_with_navigation_headers():
    response = APIClient().options(
        reverse("teams-list"),
        HTTP_ORIGIN="http://localhost:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS=("content-type,x-navigation-id,x-navigation-intent"),
    )

    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert response["Access-Control-Allow-Credentials"] == "true"
    assert "x-navigation-id" in response["Access-Control-Allow-Headers"]
    assert "x-navigation-intent" in response["Access-Control-Allow-Headers"]
