from django.db import migrations, models


def populate_goal_counts(apps, schema_editor):
    match_model = apps.get_model("matches", "Match")
    for match in match_model.objects.all().iterator():
        match.home_goal_count = match.goals.filter(team_side="home").count()
        match.away_goal_count = match.goals.filter(team_side="away").count()
        match.save(update_fields=["home_goal_count", "away_goal_count"])


class Migration(migrations.Migration):
    dependencies = [("matches", "0003_match_fixture_key")]

    operations = [
        migrations.AddField(
            model_name="match",
            name="away_goal_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="home_goal_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(populate_goal_counts, migrations.RunPython.noop),
    ]
