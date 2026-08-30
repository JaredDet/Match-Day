import uuid

import django.db.models.deletion
from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [("teams", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Player",
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
                ("name", models.CharField(max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="players",
                        to="teams.team",
                    ),
                ),
            ],
            options={
                "db_table": "players",
                "ordering": ["name"],
                "constraints": [
                    models.UniqueConstraint(
                        Lower("name"),
                        models.F("team"),
                        name="unique_player_name_per_team",
                    ),
                    models.CheckConstraint(
                        condition=~models.Q(name=""),
                        name="player_name_not_empty",
                    ),
                ],
            },
        )
    ]
