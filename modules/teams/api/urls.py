from rest_framework.routers import SimpleRouter

from modules.teams.api.views.player_view_set import PlayerViewSet
from modules.teams.api.views.team_view_set import TeamViewSet

router = SimpleRouter(use_regex_path=False)
router.register("teams", TeamViewSet, basename="teams")
router.register("players", PlayerViewSet, basename="players")

urlpatterns = router.urls
