
from django.db import models  # regular Django models
from django.contrib.gis.db import models # spatial models

class Sector(models.Model):
    sector_id = models.IntegerField()
    name = models.CharField(max_length=100)
    geom = models.GeometryField()

    class Meta:
        db_table = 'sector'  # <- force Django to use the existing table