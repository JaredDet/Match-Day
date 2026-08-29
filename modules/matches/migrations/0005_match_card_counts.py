from django.db import migrations, models


def populate_card_counts(apps, schema_editor):
    match_model = apps.get_model("matches", "Match")
    for match in match_model.objects.all().iterator():
        match.home_card_count = match.cards.filter(team_side="home").count()
        match.away_card_count = match.cards.filter(team_side="away").count()
        match.save(update_fields=["home_card_count", "away_card_count"])


class Migration(migrations.Migration):
    dependencies = [("matches", "0004_match_goal_counts")]

    operations = [
        migrations.AddField(
            model_name="match",
            name="away_card_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="home_card_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.RunPython(populate_card_counts, migrations.RunPython.noop),
    ]
