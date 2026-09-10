from uuid import UUID

from django.db.models import Count

from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.penalty_shootout import (
    PenaltyShootout,
    PenaltyShootoutKick,
    PenaltyShootoutParticipant,
)


class PenaltyShootoutRepository:
    def exists(self, match_id: UUID) -> bool:
        return PenaltyShootout.objects.filter(match_id=match_id).exists()

    def get_for_update(self, match_id: UUID) -> PenaltyShootout | None:
        return PenaltyShootout.objects.select_for_update().filter(match_id=match_id).first()

    def get_player_kick_counts(
        self,
        *,
        shootout_id: UUID,
        team_side: TeamSide,
    ) -> dict[UUID, int]:
        rows = (
            PenaltyShootoutKick.objects.filter(
                shootout_id=shootout_id,
                team_side=team_side,
            )
            .values("player_id")
            .annotate(kick_count=Count("id"))
        )

        return {row["player_id"]: row["kick_count"] for row in rows}

    def list_participant_ids(
        self,
        *,
        shootout_id: UUID,
        team_side: TeamSide,
    ) -> set[UUID]:
        return set(
            PenaltyShootoutParticipant.objects.filter(
                shootout_id=shootout_id,
                team_side=team_side,
                is_eligible=True,
            ).values_list("player_id", flat=True)
        )

    def get_participant_for_update(
        self,
        *,
        shootout_id: UUID,
        player_id: UUID,
    ) -> PenaltyShootoutParticipant | None:
        return (
            PenaltyShootoutParticipant.objects.select_for_update()
            .filter(
                shootout_id=shootout_id,
                player_id=player_id,
            )
            .first()
        )

    def get_eligible_counts(self, shootout_id: UUID) -> dict[TeamSide, int]:
        rows = (
            PenaltyShootoutParticipant.objects.filter(
                shootout_id=shootout_id,
                is_eligible=True,
            )
            .values("team_side")
            .annotate(participant_count=Count("id"))
        )
        counts = {TeamSide.HOME: 0, TeamSide.AWAY: 0}
        counts.update({TeamSide(row["team_side"]): row["participant_count"] for row in rows})
        return counts

    def save(self, shootout: PenaltyShootout) -> None:
        shootout.save()

    def save_kick(self, kick: PenaltyShootoutKick) -> None:
        kick.save()

    def save_participants(
        self,
        participants: list[PenaltyShootoutParticipant],
    ) -> None:
        PenaltyShootoutParticipant.objects.bulk_create(participants)

    def save_participant(self, participant: PenaltyShootoutParticipant) -> None:
        participant.save(
            update_fields=[
                "is_eligible",
                "ineligibility_reason",
                "became_ineligible_at",
            ]
        )
