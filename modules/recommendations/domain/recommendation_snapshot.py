from django.db import models


class RecommendationSnapshot(models.Model):
    key = models.CharField(primary_key=True, max_length=36)
    visitor = models.OneToOneField("recommendations.Visitor", null=True, on_delete=models.CASCADE)
    sections = models.JSONField(default=dict)
    generated_at = models.DateTimeField()
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "recommendation_snapshots"
