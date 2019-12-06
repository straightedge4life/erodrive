from django.urls import path, include
from web import views


urlpatterns = [
    path('', views.index, name='index'),
    path('detail', views.detail, name='detail'),
    path('login', views.login, name='login'),
]
