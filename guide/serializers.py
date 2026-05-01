from rest_framework import serializers
from .models import Sector, Area, SubArea, Route

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['sector_id', 'name', 'description','boundary', 'centroid']

class RouteSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source="area.name", read_only=True)
    subarea_name = serializers.CharField(source="subarea.name", read_only=True)
    
    class Meta:
        model = Route
        fields = ['route_id',
                  'area_name',
                  'subarea_name',
                  'area',
                  'crag_order', 
                  'centroid', 
                  'name', 
                  'type', 
                  'description', 
                  'grade', 
                  'subarea',    
                  'danger_rating', 
                  'star_rating', 
                  'centroid', 
                  'height', 
                  'first_ascencionist', 
                  'fa_year']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['area_id', 'sector', 'boundary', 'centroid', 'name', 'description', 'directions', 'approach_time', 'drive_time', 'aspect']

class SubAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubArea
        fields = ['subarea_id', 'area', 'centroid', 'name', 'description', 'aspect']
