from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import django_filters

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
        fields = ["area_id", "subarea_id"]

class RouteListView(generics.ListAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RouteFilter
    search_fields = ["name", "grade", "type"]
    ordering_fields = ["name", "grade", "type"]

'''
def aspect_calculator(aspect):
    aspect_mapping = {
        'north': ['Morning': False, 'Afternoon': False, 'Evening': False],
        'northeast': ['Morning': True, 'Afternoon': False, 'Evening': False],
        'east': ['Morning': True, 'Afternoon': False, 'Evening': False],
        'southeast': ['Morning': True, 'Afternoon': True, 'Evening': False],
        'south': ['Morning': True, 'Afternoon': True, 'Evening': True],
        'southwest': ['Morning': False, 'Afternoon': True, 'Evening': True],
        'west': ['Morning': False, 'Afternoon': False, 'Evening': True],
        'northwest': ['Morning': False, 'Afternoon': False, 'Evening': True],
    }
    return aspect_mapping.get(aspect.upper(), None)
'''