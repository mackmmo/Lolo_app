
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
'''
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

class SubArea(models.Model):
    subarea_id = models.IntegerField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='area_id')  # Assuming a subarea belongs to an area
    name = models.CharField(max_length=100)
    #image = models.URLField()  # Assuming you want to store an image URL for the subarea
    description = models.TextField()

    class Meta:
        db_table = 'subarea'  # <- force Django to use the existing table

class Routes(models.Model):
    route_id = models.IntegerField(primary_key=True)
    subarea = models.ForeignKey(SubArea, on_delete=models.CASCADE, db_column='subarea_id')  # Assuming a route belongs to a subarea
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)  # Assuming grade is a string like "5.10a"
    danger_rating = models.CharField(max_length=10)  # Assuming danger rating is a string like "E1", "E2", "E3"
    fa = models.CharField(max_length=100)  # First ascensionist
    fa_year = models.IntegerField()  # Year of first ascent
    coordinates = geomodels.PointField(srid=3857)  # Assuming the coordinates are a point (e.g., start of the route)
    description = models.TextField()

    class Meta:
        db_table = 'routes'  # <- force Django to use the existing table

class Parking(models.Model):   
    parking_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = geomodels.PointField(srid=3857)  # Assuming the parking location is a point

    class Meta:
        db_table = 'parking'  # <- force Django to use the existing table

class StartPoints(models.Model):
    start_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    location = geomodels.PointField(srid=3857)  # Assuming the start point location is a point

    class Meta:
        db_table = 'start_points'  # <- force Django to use the existing table

class Camping(models.Model):
    camping_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = geomodels.PointField(srid=3857)  # Assuming the camping location is a point

    class Meta:
        db_table = 'camping'  # <- force Django to use the existing table

class Restroom(models.Model):
    restroom_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = geomodels.PointField(srid=3857)  # Assuming the restroom location is a point

    class Meta:
        db_table = 'restroom'  # <- force Django to use the existing table
'''