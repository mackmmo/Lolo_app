# api/urls.py
from django.urls import path
from .views import ExampleAPIView

urlpatterns = [
    path('example/', views.example_view, name='example'),
]