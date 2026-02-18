# api/urls.py
from django.urls import path
from .views import ExampleAPIView

urlpatterns = [
    path('example/', ExampleAPIView.as_view(), name='example'),
]