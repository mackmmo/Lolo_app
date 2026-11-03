from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("guide", "0005_standing_route_lists"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="OfflineReceipt", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("request_id", models.UUIDField()),
            ("fingerprint", models.CharField(max_length=64)),
            ("status", models.PositiveSmallIntegerField()),
            ("response", models.JSONField(null=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.AddConstraint(model_name="offlinereceipt", constraint=models.UniqueConstraint(fields=("user", "request_id"), name="unique_offline_request")),
    ]
