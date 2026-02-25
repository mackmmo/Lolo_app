from rest_framework import serializers
from .models import Area, Parking, Roads, Routes, Sector, SubArea

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['sector_id', 'name', 'description']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['area_id', 'sector', 'boundary', 'centroid', 'name', 'description']

class SubAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubArea
        fields = ['subarea_id', 'area', 'name', 'boundary', 'centroid', 'description']

class RoutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routes
        fields = ['route_id', 'subarea', 'name', 'grade', 'danger_rating', 'fa', 'fa_year', 'coordinates', 'description']

class RoadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roads
        fields = ['road_id', 'name', 'description', 'path', 'distance']

class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = ['parking_id', 'name', 'description', 'location']

class SectorDetailSerializer(serializers.ModelSerializer):
    areas = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Sector
        fields = ['sector_id', 'name', 'description', 'areas']  

class AreaDetailSerializer(serializers.ModelSerializer):
    # include nested sector data as well as subareas for the detail view
    sector = SectorSerializer(read_only=True)
    subareas = SubAreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['area_id', 'sector', 'boundary', 'centroid', 'name', 'description', 'subareas']   

