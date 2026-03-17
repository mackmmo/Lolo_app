from rest_framework import serializers
from .models import Sector, Area

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['sector_id', 'name', 'description','boundary', 'centroid']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['area_id', 'sector', 'boundary', 'centroid', 'name', 'description']
