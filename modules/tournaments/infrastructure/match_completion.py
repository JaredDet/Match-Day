import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from modules.matches.domain.match import Match, MatchStatus
from modules.matches.domain.penalty_shootout import PenaltyShootout

logger = logging.getLogger(__name__)


def advance_for_match(match_id):
    from core.dependency_injector import injector_instance
    from modules.tournaments.application.commands.advance_bracket_use_case import (
        AdvanceBracketUseCase,
    )
    from modules.tournaments.infrastructure.repository.bracket_repository import BracketRepository

    try:
        season_id = injector_instance.get(BracketRepository).season_for_match(match_id)

        if season_id is None:
            return

        injector_instance.get(AdvanceBracketUseCase).execute(season_id=season_id)
    except Exception:
        # El resultado ya está confirmado. La acción advance permite reintentar sin duplicar cruces.
        logger.exception("No se pudo avanzar el cuadro asociado al partido %s", match_id)


@receiver(post_save, sender=Match, dispatch_uid="tournaments.match_finished")
def on_match_saved(sender, instance, raw=False, **kwargs):
    if not raw and instance.status in (MatchStatus.LIVE, MatchStatus.FINISHED):
        transaction.on_commit(lambda: advance_for_match(instance.id))


@receiver(post_save, sender=PenaltyShootout, dispatch_uid="tournaments.shootout_finished")
def on_shootout_saved(sender, instance, raw=False, **kwargs):
    if not raw and instance.status == "finished":
        transaction.on_commit(lambda: advance_for_match(instance.match_id))
