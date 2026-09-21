from modules.recommendations.domain.interest_profile import InterestProfile
from modules.recommendations.domain.recommendation_snapshot import RecommendationSnapshot


class RecommendationRepository:
    def save_profile(self, visitor_id, profile, now):
        InterestProfile.objects.update_or_create(
            visitor_id=visitor_id,
            defaults={
                "team_weights": profile.teams,
                "tournament_weights": profile.tournaments,
                "computed_at": now,
            },
        )

    def save_snapshot(self, visitor_id, sections, now, expires_at):
        RecommendationSnapshot.objects.update_or_create(
            key=str(visitor_id) if visitor_id else "general",
            defaults={
                "visitor_id": visitor_id,
                "sections": sections,
                "generated_at": now,
                "expires_at": expires_at,
            },
        )
