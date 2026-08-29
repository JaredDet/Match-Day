from datetime import UTC
from hashlib import sha256

from django.db import migrations, models


def populate_fixture_keys(apps, schema_editor):
    match_model = apps.get_model("matches", "Match")
    for match in match_model.objects.all().iterator():
        teams = sorted(
            (match.home_team_name.strip().casefold(), match.away_team_name.strip().casefold())
        )
        instant = match.scheduled_at.astimezone(UTC).isoformat()
        payload = f"{teams[0]}\0{teams[1]}\0{instant}"
        match.fixture_key = sha256(payload.encode()).hexdigest()
        match.save(update_fields=["fixture_key"])


class Migration(migrations.Migration):
    dependencies = [("matches", "0002_card_goal")]

    operations = [
        migrations.AddField(
            model_name="match",
            name="fixture_key",
            field=models.CharField(editable=False, max_length=64, null=True),
        ),
        migrations.RunPython(populate_fixture_keys, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="match",
            name="fixture_key",
            field=models.CharField(editable=False, max_length=64, unique=True),
        ),
    ]
