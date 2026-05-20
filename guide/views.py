from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import django_filters
from django.http import HttpResponse
from django.db import connection
from .models import Sector, Area, SubArea, Route
from .serializers import SectorSerializer, AreaSerializer, SubAreaSerializer, RouteSerializer
    
class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all().order_by('sector_id')
    serializer_class = SectorSerializer

class AreaListView(generics.ListAPIView):
    queryset = Area.objects.all().order_by('area_id')
    serializer_class = AreaSerializer

class SubAreaListView(generics.ListAPIView):
    queryset = SubArea.objects.all().order_by('subarea_id')
    serializer_class = SubAreaSerializer

class RouteDetailView(generics.RetrieveAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class RouteFilter(django_filters.FilterSet):
    min_grade = django_filters.NumberFilter(field_name="grade_index", lookup_expr="gte")
    max_grade = django_filters.NumberFilter(field_name="grade_index", lookup_expr="lte")
    area = django_filters.CharFilter(field_name="area__name", lookup_expr="icontains")
    subarea = django_filters.CharFilter(field_name="subarea__name", lookup_expr="icontains")

    class Meta:
        model = Route
        fields = ["area", "subarea"]

class RouteListView(generics.ListAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RouteFilter
    search_fields = ["name", "grade", "type"]
    ordering_fields = ["name", "grade", "type"]

# Vector tile endpoint for areas
def area_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                area_id,
                name,
                ST_AsMVTGeom(
                  boundary,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM area
              WHERE boundary && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'areas', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for roads
def road_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                road_id,
                roadname,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM roads
              WHERE geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'roads', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for trails
def trail_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                trail_id,
                approach,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM trails
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'trails', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for pois
def poi_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                poi_id,
                name,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM pois
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'poi', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for trailheads
def trailhead_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                trailhead_id,
                name,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM trailheads
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'trailheads', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )

# Vector tile endpoint for gates
def gate_tiles(request, z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH mvtgeom AS (
              SELECT
                gate_id,
                name,
                description,
                ST_AsMVTGeom(
                  wkb_geometry,
                  ST_TileEnvelope(%s, %s, %s),
                  4096,
                  64,
                  true
                ) AS geom
              FROM gates
              WHERE wkb_geometry && ST_TileEnvelope(%s, %s, %s)
            )
            SELECT ST_AsMVT(mvtgeom, 'gates', 4096, 'geom')
            FROM mvtgeom
        """, [z, x, y, z, x, y])
        row = cursor.fetchone()

    return HttpResponse(
        bytes(row[0]) if row and row[0] else b"",
        content_type="application/vnd.mapbox-vector-tile"
    )