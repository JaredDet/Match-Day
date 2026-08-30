from django.db import migrations, models


def populate_team_name_snapshots(apps, schema_editor):
    match_model = apps.get_model("matches", "Match")
    for match in match_model.objects.select_related("home_team", "away_team").iterator():
        match.home_team_name = match.home_team.name
        match.away_team_name = match.away_team.name
        match.save(update_fields=["home_team_name", "away_team_name"])


class Migration(migrations.Migration):
    dependencies = [("matches", "0009_normalize_match_teams")]

    operations = [
        migrations.AddField(
            model_name="match",
            name="away_team_name",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="match",
            name="home_team_name",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.RunPython(populate_team_name_snapshots, migrations.RunPython.noop),
    ]
