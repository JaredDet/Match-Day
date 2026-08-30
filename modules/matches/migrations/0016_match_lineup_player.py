import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("matches", "0015_move_lineup_to_match"),
        ("teams", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MatchLineupPlayer",
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
                ("shirt_number", models.PositiveSmallIntegerField()),
                ("is_captain", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lineup_players",
                        to="matches.match",
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="match_lineups",
                        to="teams.player",
                    ),
                ),
            ],
            options={
                "db_table": "match_lineup_players",
                "ordering": ["team_side", "shirt_number"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("match", "player"),
                        name="unique_player_per_match_lineup",
                    ),
                    models.UniqueConstraint(
                        fields=("match", "team_side", "shirt_number"),
                        name="unique_shirt_per_match_team",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(is_captain=True),
                        fields=("match", "team_side"),
                        name="unique_captain_per_match_team",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(team_side__in=["home", "away"]),
                        name="valid_lineup_player_team_side",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(shirt_number__gte=1, shirt_number__lte=99),
                        name="valid_lineup_shirt_number",
                    ),
                ],
            },
        )
    ]
