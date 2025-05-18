from django.contrib import admin
from django.urls import path, include
from app_home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_home.urls')),
]
