from rest_framework.routers import SimpleRouter

from modules.news.api.views.news_view_set import NewsViewSet

router = SimpleRouter(use_regex_path=False)
router.register("news", NewsViewSet, basename="news")

urlpatterns = router.urls
