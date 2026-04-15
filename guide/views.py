# guide/views.py
from rest_framework import generics
from .models import Sector, Area, SubArea, Route
from .serializers import SectorSerializer, AreaSerializer, SubAreaSerializer, RouteSerializer
from django.http import JsonResponse

class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all().order_by('sector_id')
    serializer_class = SectorSerializer

class AreaListView(generics.ListAPIView):
    queryset = Area.objects.all().order_by('area_id')
    serializer_class = AreaSerializer

class SubAreaListView(generics.ListAPIView):
    queryset = SubArea.objects.all().order_by('subarea_id')
    serializer_class = SubAreaSerializer
    
class RouteListView(generics.ListAPIView):
    queryset = Route.objects.all().order_by('route_id')
    serializer_class = RouteSerializer