from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("guide", "0004_repeat_send_style")]
    operations = [migrations.AddField(model_name="juntmastersstanding", name="scored_routes", field=models.JSONField(default=list))]
