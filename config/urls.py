"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from guide.views import SectorListView, db_debug  # import the view
from api.views import ExampleAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sectors/', SectorListView.as_view(), name='sector-list'),
    path('db-debug/', db_debug, name='db-debug'),
    path('api/', include('api.urls')),  # include API URLs
]