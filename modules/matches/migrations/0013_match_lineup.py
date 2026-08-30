import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("matches", "0012_match_stadium_and_referee")]

    operations = [
        migrations.CreateModel(
            name="MatchLineup",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "team_side",
                    models.CharField(choices=[("home", "Home"), ("away", "Away")], max_length=10),
                ),
                ("formation", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lineups",
                        to="matches.match",
                    ),
                ),
            ],
            options={
                "db_table": "match_lineups",
                "ordering": ["team_side"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("match", "team_side"),
                        name="unique_lineup_per_match_team_side",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("team_side__in", ["home", "away"])),
                        name="valid_lineup_team_side",
                    ),
                    models.CheckConstraint(
                        condition=~models.Q(formation=""),
                        name="lineup_formation_not_empty",
                    ),
                ],
            },
        )
    ]
