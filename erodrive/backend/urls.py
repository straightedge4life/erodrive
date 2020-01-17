from django.urls import path, include
from backend import views

urlpatterns = [
    path('install', views.install, name='install'),
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('upload', views.upload, name='upload'),
]
