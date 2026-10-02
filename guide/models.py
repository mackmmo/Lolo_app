
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
    pro = models.CharField(max_length=50)
    description = models.TextField()
    grade = models.CharField(max_length=50)
    
    subarea = models.ForeignKey(SubArea, 
                                on_delete=models.SET_NULL,
                                related_name='routes',
                                null=True, 
                                blank=True,
                                db_column='subarea_id')
    
    area = models.ForeignKey(Area, 
                             on_delete=models.CASCADE, 
                             db_column='area_id') 
    
    danger_rating = models.CharField(max_length=50)
    star_rating = models.IntegerField()

    centroid = geomodels.PointField(srid=3857)
    height = models.IntegerField()
    first_ascencionist = models.CharField(max_length=100)
    fa_year = models.IntegerField() 
    grade_index = models.IntegerField()
    class Meta:
        db_table = 'route' 
        ordering = ['subarea__area_id', 'subarea_id', 'crag_order', 'route_id']


from django.contrib.auth.models import User

class RouteLog(models.Model):
    STATUS_CHOICES = [
        ("project", "Project"),
        ("sent", "Sent"),
    ]

    SEND_STYLE_CHOICES = [
        ("onsight", "Onsight"),
        ("flash", "Flash"),
        ("redpoint", "Redpoint"),
        ("pinkpoint", "Pinkpoint"),
    ]

    log_id = models.BigAutoField(primary_key=True)

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        db_column="route_id",
        related_name="user_logs"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="route_logs"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="project"
    )

    send_style = models.CharField(
        max_length=20,
        choices=SEND_STYLE_CHOICES,
        null=True,
        blank=True
    )

    date_sent = models.DateField(null=True, blank=True)

    beta = models.TextField(null=True, blank=True)

    attempts = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "route_log"
        managed = False
        constraints = [
            models.UniqueConstraint(
                fields=["user", "route"],
                name="unique_user_route_log"
            )
        ]

class RouteTodo(models.Model):
    todo_id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="route_todos",
    )

    route = models.ForeignKey(
        "Route",
        on_delete=models.CASCADE,
        db_column="route_id",
        related_name="user_todos",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "route_todo"
        managed = False
        constraints = [
            models.UniqueConstraint(
                fields=["user", "route"],
                name="unique_user_route_todo",
            )
        ]


class RouteComment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="route_comments",
    )

    route = models.ForeignKey(
        "Route",
        on_delete=models.CASCADE,
        db_column="route_id",
        related_name="comments",
    )

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "route_comment"
        managed = False