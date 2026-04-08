from rest_framework import serializers
from .models import Sector, Area, SubArea

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['sector_id', 'name', 'description','boundary', 'centroid']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['area_id', 'sector', 'boundary', 'centroid', 'name', 'description', 'directions', 'approach_time', 'drive_time', 'aspect']

class SubAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubArea
        fields = ['subarea_id', 'area', 'centroid', 'name', 'description', 'aspect']