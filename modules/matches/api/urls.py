from rest_framework.routers import SimpleRouter

from modules.matches.api.views.match_view_set import MatchViewSet

router = SimpleRouter(use_regex_path=False)
router.register("matches", MatchViewSet, basename="matches")

urlpatterns = router.urls
