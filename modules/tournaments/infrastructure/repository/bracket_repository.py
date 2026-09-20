from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.phase import Phase, PhaseKind


class BracketRepository:
    def phases(self, season_id):
        return list(Phase.objects.filter(season_id=season_id).order_by("order", "id"))

    def fixtures(self, phase_id):
        return list(
            Fixture.objects.filter(phase_id=phase_id)
            .select_related("match__penalty_shootout")
            .order_by("position", "id")
        )

    def has_knockout(self, season_id):
        return Phase.objects.filter(season_id=season_id).exclude(kind=PhaseKind.GROUPS).exists()

    def season_for_match(self, match_id):
        return (
            Fixture.objects.filter(match_id=match_id, phase__generated=True)
            .values_list("phase__season_id", flat=True)
            .first()
        )
