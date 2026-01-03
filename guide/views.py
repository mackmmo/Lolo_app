# guide/serializers.py
from rest_framework import generics
from .models import Sector
from .serializers import SectorSerializer

class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all().order_by('sector_id')
    serializer_class = SectorSerializer
