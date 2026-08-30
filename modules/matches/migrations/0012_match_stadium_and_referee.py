from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("matches", "0011_normalize_event_players")]

    operations = [
        migrations.AddField(
            model_name="match",
            name="referee_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="match",
            name="stadium_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
