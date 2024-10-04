from django.urls import path
from . import views
from .models import Ingreso, Persona, Categoria
from django.utils import timezone
from django.views import View
from .views import GastoView,CategoriaView,EliminarGastoView
urlpatterns = [
    path('', views.home, name='home'),

    path('ingresos/', views.ingresos, name='ingresos'),

    #Gastos
    
    path('registrar/gasto/', GastoView.as_view(), name='registrar_gasto'),
    path('registrar/gasto/bajaGasto', EliminarGastoView.as_view(), name='baja_Gasto'),

    path('registrar/gasto/cargarCategoria', CategoriaView.as_view(), name='cargar_categoria'),
    
    



]