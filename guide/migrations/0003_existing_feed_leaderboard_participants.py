from django.db import migrations


class Migration(migrations.Migration):
    # Keep this migration name compatible with databases that have applied it.
    # Publication remains opt-in; do not automatically enroll feed-sharing users.
    dependencies = [("guide", "0002_publication_competitions")]
    operations = []
