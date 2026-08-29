from rest_framework.routers import DefaultRouter

from modules.matches.api.views.match_view_set import MatchViewSet

router = DefaultRouter()
router.register("matches", MatchViewSet, basename="matches")

urlpatterns = router.urls
