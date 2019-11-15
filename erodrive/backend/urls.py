from django.urls import path, include
from backend import views

urlpatterns = [
    path('install', views.install, name='install'),
]
