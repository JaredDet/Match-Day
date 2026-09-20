from rest_framework.routers import SimpleRouter

from modules.tournaments.api.views.fixture_view_set import FixtureViewSet
from modules.tournaments.api.views.group_entry_view_set import GroupEntryViewSet
from modules.tournaments.api.views.group_view_set import GroupViewSet
from modules.tournaments.api.views.phase_view_set import PhaseViewSet
from modules.tournaments.api.views.season_view_set import SeasonViewSet
from modules.tournaments.api.views.tournament_view_set import TournamentViewSet

router = SimpleRouter(use_regex_path=False)
router.register("tournaments", TournamentViewSet, basename="tournaments")
router.register("tournament-seasons", SeasonViewSet, basename="tournament-seasons")
router.register("tournament-phases", PhaseViewSet, basename="tournament-phases")
router.register("tournament-groups", GroupViewSet, basename="tournament-groups")
router.register("tournament-group-entries", GroupEntryViewSet, basename="tournament-group-entries")
router.register("tournament-fixtures", FixtureViewSet, basename="tournament-fixtures")
urlpatterns = router.urls
