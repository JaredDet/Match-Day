from rest_framework.routers import SimpleRouter

from modules.teams.api.views.team_view_set import TeamViewSet

router = SimpleRouter(use_regex_path=False)
router.register("teams", TeamViewSet, basename="teams")

urlpatterns = router.urls
