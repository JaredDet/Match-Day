from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("matches", "0005_match_card_counts")]

    operations = [
        migrations.AddField(
            model_name="goal",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
