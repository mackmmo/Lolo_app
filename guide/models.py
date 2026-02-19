
from django.db import models as djmodels  # regular Django models
from django.contrib.gis.db import models as GISmodels # spatial models

class Sector(djmodels.Model):
    sector_id = djmodels.IntegerField()
    name = djmodels.CharField(max_length=100)
    description = djmodels.TextField()

    class Meta:
        db_table = 'sector'  # <- force Django to use the existing table

class FutureModes(GISmodels.Model):
    geom = GISmodels.GeometryField()