from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("matches", "0007_card_cancelled_at")]

    operations = [
        migrations.RenameField(
            model_name="goal",
            old_name="cancelled_at",
            new_name="disallowed_at",
        ),
        migrations.RenameField(
            model_name="card",
            old_name="cancelled_at",
            new_name="rescinded_at",
        ),
    ]
