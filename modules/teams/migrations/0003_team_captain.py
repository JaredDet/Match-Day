import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teams", "0002_player"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="captain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="captained_teams",
                to="teams.player",
            ),
        ),
    ]
