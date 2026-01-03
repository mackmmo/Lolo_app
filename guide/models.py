from django.db import models


# apps.py must include this app; settings must use the PostGIS backend and django.contrib.gis
from django.contrib.gis.db import models  # <-- GeoDjango models (not django.db.models)
from django.core.exceptions import ValidationError


class Sector(models.Model):
    sector_id = models.AutoField(primary_key=True, db_column="sector_id")
    name = models.TextField(db_column="name", unique=True)
    description = models.TextField(db_column="description", blank=True, null=True)

    class Meta:
        db_table = "sector"
        managed = False

    def __str__(self):
        return self.name


class Area(models.Model):
    area_id = models.AutoField(primary_key=True, db_column="area_id")
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        db_column="sector_id",
        related_name="areas",
    )
    name = models.TextField(db_column="name")
    description = models.TextField(db_column="description", blank=True, null=True)
    # polygon + optional label point
    boundary = models.MultiPolygonField(db_column="boundary", srid=4326)
    label_pt = models.PointField(db_column="label_pt", srid=4326, blank=True, null=True)

    class Meta:
        db_table = "area"
        managed = False
        constraints = [
            models.UniqueConstraint(fields=["sector", "name"], name="area_sector_name_uniq")
        ]

    def __str__(self):
        return self.name


class SubArea(models.Model):
    subarea_id = models.AutoField(primary_key=True, db_column="subarea_id")
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        db_column="area_id",
        related_name="subareas",
    )
    name = models.TextField(db_column="name")
    description = models.TextField(db_column="description", blank=True, null=True)
    # polygon + optional label point (what you asked for)
    boundary = models.MultiPolygonField(db_column="boundary", srid=4326)
    label_pt = models.PointField(db_column="label_pt", srid=4326, blank=True, null=True)

    class Meta:
        db_table = "subarea"
        managed = False
        constraints = [
            models.UniqueConstraint(fields=["area", "name"], name="subarea_area_name_uniq")
        ]

    def __str__(self):
        return self.name


class Wall(models.Model):
    wall_id = models.AutoField(primary_key=True, db_column="wall_id")
    # Optional level: a wall can belong to either a subarea OR an area (both nullable).
    subarea = models.ForeignKey(
        SubArea,
        on_delete=models.SET_NULL,
        db_column="subarea_id",
        related_name="walls",
        blank=True,
        null=True,
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        db_column="area_id",
        related_name="walls",
        blank=True,
        null=True,
    )
    name = models.TextField(db_column="name")
    description = models.TextField(db_column="description", blank=True, null=True)
    morning_sun = models.BooleanField(db_column="morning_sun", default=False)
    afternoon_sun = models.BooleanField(db_column="afternoon_sun", default=False)

    class Meta:
        db_table = "wall"
        managed = False

    def clean(self):
        # Mirror your SQL CHECK: at least one of subarea_id or area_id must be set
        if not self.subarea and not self.area:
            raise ValidationError("Wall must be linked to a SubArea or an Area.")

    def __str__(self):
        return self.name


class WallSun(models.Model):
    """Unmanaged model mapped to your view wall_sun."""
    wall_id = models.IntegerField(primary_key=True, db_column="wall_id")
    name = models.TextField(db_column="name")
    sun_definition = models.TextField(db_column="sun_definition")

    class Meta:
        db_table = "wall_sun"
        managed = False


class Route(models.Model):
    route_id = models.AutoField(primary_key=True, db_column="route_id")
    wall = models.ForeignKey(
        Wall,
        on_delete=models.CASCADE,
        db_column="wall_id",
        related_name="routes",
        blank=True,
        null=True,
    )
    name = models.TextField(db_column="name")
    type = models.TextField(db_column="type", blank=True, null=True)        # 'trad','sport','mixed','boulder'
    grade_text = models.TextField(db_column="grade_text", blank=True, null=True)  # '5.10b', 'V6', etc.
    aspect = models.TextField(db_column="aspect", blank=True, null=True)    # 'N','S','E','W'
    geom = models.PointField(db_column="geom", srid=4326)

    class Meta:
        db_table = "route"
        managed = False
        indexes = [
            models.Index(fields=["type"], name="route_type_idx_dj"),
            models.Index(fields=["grade_text"], name="route_grade_idx_dj"),
            models.Index(fields=["aspect"], name="route_aspect_idx_dj"),
            # Spatial index is created in SQL already; Django won’t modify it since managed=False
        ]

    def __str__(self):
        return self.name