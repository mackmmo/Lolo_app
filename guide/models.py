
from django.db import models  # regular Django models

class Sector(models.Model):
    sector_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        db_table = 'sector'  # <- force Django to use the existing table
