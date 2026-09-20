import pytest

from core.exceptions import AppException
from modules.tournaments.domain.tournament import Tournament
from modules.tournaments.infrastructure.repository.tournament_repository import TournamentRepository

pytestmark = pytest.mark.django_db


def test_duplicate_slug_maps_to_conflict_and_keeps_transaction_usable():
    repository = TournamentRepository()
    data = dict(slug="copa", name="Copa", country="Chile", category="Nacional")
    repository.save(Tournament.create(**data))

    with pytest.raises(AppException) as error:
        repository.save(Tournament.create(**data))

    assert error.value.code == "tournament_already_exists"
    assert Tournament.objects.count() == 1
