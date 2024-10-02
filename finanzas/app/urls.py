from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ingresos/', views.ingresos, name='ingresos'),
    path('gastos/', views.gastos, name='gastos'),
]