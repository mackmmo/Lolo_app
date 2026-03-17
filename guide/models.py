
from django.db import models  # regular Django models
from django.contrib.gis.db import models as geomodels  # for GIS-enabled models, if needed

class Sector(models.Model):
    sector_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    boundary = geomodels.MultiPolygonField(srid=3857)  # Assuming the boundary is a polygon
    centroid = geomodels.PointField(srid=3857)  # Assuming the centroid is a point

    class Meta:
        db_table = 'sector'  # <- force Django to use the existing table

class Area(models.Model):
    area_id = models.IntegerField(primary_key=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, db_column='sector_id')  # Assuming an area belongs to a sector
    boundary = geomodels.MultiPolygonField(srid=3857)  # Assuming the boundary is a polygon
    centroid = geomodels.PointField(srid=3857)  # Assuming the centroid is a point
    name = models.CharField(max_length=100)
    description = models.TextField()
    #image = models.URLField()  # Assuming you want to store an image URL for the area

    class Meta:
        db_table = 'area'  # <- force Django to use the existing table

