
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
    directions = models.TextField() 
    approach_time = models.IntegerField()
    drive_time = models.IntegerField()
    aspect = models.CharField(max_length=100)  # Assuming aspect is a string field
    #image = models.URLField()  # Assuming you want to store an image URL for the area

    class Meta:
        db_table = 'area'  # <- force Django to use the existing table

class SubArea(models.Model):
    subarea_id = models.IntegerField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='area_id')  # Assuming a subarea belongs to an area
    centroid = geomodels.PointField(srid=3857)  # Assuming the centroid is a point
    name = models.CharField(max_length=100)
    description = models.TextField()
    aspect = models.CharField(max_length=100)  # Assuming aspect is a string field
    #image = models.URLField()  # Assuming you want to store an image URL for the subarea

    class Meta:
        db_table = 'subarea'  # <- force Django to use the existing table

class Route(models.Model):
    route_id = models.IntegerField(primary_key=True)
    crag_order = models.IntegerField()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    description = models.TextField()
    grade = models.CharField(max_length=50)
    subarea = models.ForeignKey(SubArea, on_delete=models.CASCADE, db_column='subarea_id')
    danger_rating = models.CharField(max_length=50)
    star_rating = models.IntegerField()
    centroid = geomodels.PointField(srid=3857)
    height = models.IntegerField()
    first_ascencionist = models.CharField(max_length=100)
    fa_year = models.IntegerField() 


