import uuid

from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Team",
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
            ],
            options={
                "db_table": "teams",
                "ordering": ["name"],
                "constraints": [
                    models.UniqueConstraint(
                        Lower("name"),
                        name="unique_team_name_case_insensitive",
                    ),
                    models.CheckConstraint(
                        condition=~models.Q(name=""),
                        name="team_name_not_empty",
                    ),
                ],
            },
        )
    ]
