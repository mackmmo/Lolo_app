from django.db import migrations, models


CHOICES = [("onsight", "Onsight"), ("flash", "Flash"), ("redpoint", "Redpoint"), ("pinkpoint", "Pinkpoint"), ("repeat", "Repeat")]


class Migration(migrations.Migration):
    dependencies = [("guide", "0003_existing_feed_leaderboard_participants")]
    operations = [
        migrations.AlterField(model_name="competitionsend", name="send_style",
            field=models.CharField(blank=True, null=True, max_length=20, choices=CHOICES)),
        migrations.SeparateDatabaseAndState(database_operations=[], state_operations=[
            migrations.AlterField(model_name="routelog", name="send_style",
                field=models.CharField(blank=True, null=True, max_length=20, choices=CHOICES)),
        ]),
    ]
