import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("teams", "0006_team_city_team_crest_team_founded_year_and_more")]
    operations = [
        migrations.CreateModel(
            name="TeamFormation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=80)),
                ("shape", models.CharField(choices=[("4-3-3", "4-3-3"), ("4-4-2", "4-4-2"), ("4-2-3-1", "4-2-3-1"), ("4-1-4-1", "4-1-4-1"), ("3-5-2", "3-5-2"), ("3-4-3", "3-4-3")], max_length=10)),
                ("positions", models.JSONField()),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="formations", to="teams.team")),
            ],
            options={"db_table": "team_formations", "ordering": ["name", "id"]},
        ),
        migrations.AddConstraint(model_name="teamformation", constraint=models.UniqueConstraint(fields=("team", "name"), name="unique_team_formation_name")),
        migrations.AddConstraint(model_name="teamformation", constraint=models.UniqueConstraint(condition=models.Q(("is_default", True)), fields=("team",), name="unique_default_formation_per_team")),
    ]
