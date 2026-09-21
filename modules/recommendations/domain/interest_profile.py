from django.db import models


class InterestProfile(models.Model):
    visitor = models.OneToOneField(
        "recommendations.Visitor", primary_key=True, on_delete=models.CASCADE
    )
    team_weights = models.JSONField(default=dict)
    tournament_weights = models.JSONField(default=dict)
    computed_at = models.DateTimeField()

    class Meta:
        db_table = "recommendation_interest_profiles"
