from rest_framework.routers import SimpleRouter

from modules.recommendations.api.views.recommendation_view_set import RecommendationViewSet

router = SimpleRouter(use_regex_path=False)
router.register("recommendations", RecommendationViewSet, basename="recommendations")
urlpatterns = router.urls
