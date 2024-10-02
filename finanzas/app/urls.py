from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('prueba/', views.Prueba, name='prueba'),
]