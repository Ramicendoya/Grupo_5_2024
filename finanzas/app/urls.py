from django.urls import path
from . import views
from django.utils import timezone
from django.views import View
from .views import GastoView,CategoriaView,EliminarGastoView,EditarIngresoView, CategoriaView, IngresoView, EliminarIngreso, ObtenerIngresoView, ObtenerGastoView, EditarGastoView

urlpatterns = [
    path('', views.home, name='home'),


    #Gastos
    path('registrar/gasto/', GastoView.as_view(), name='registrar_gasto'),
    path('registrar/<str:origen>/cargarCategoria/', CategoriaView.as_view(), name='cargar_categoria'),
    path('gastos/eliminar/<int:gasto_pk>/', EliminarGastoView.as_view(), name='eliminar_gasto'),
    path('gastos/obtener/<int:gasto_pk>/', ObtenerGastoView.as_view(), name='obtener_gasto'),
    path('gastos/editar/<int:gasto_pk>/', EditarGastoView.as_view(), name='editar_gasto'),


    # Registrar Ingresos
    path('registrar/ingreso/', IngresoView.as_view(), name='registrar_ingreso'),
    path('registrar/ingreso/<int:ingreso_pk>/eliminar', EliminarIngreso.as_view(), name='eliminar_ingreso'),
    path('registrar/<str:origen>/cargarCategoria/', CategoriaView.as_view(), name='cargar_categoria'),
    path('ingresos/obtener/<int:ingreso_pk>/', ObtenerIngresoView.as_view(), name='obtener_ingreso'),
    path('ingresos/editar/<int:ingreso_pk>/', EditarIngresoView.as_view(), name='editar_ingreso'),


]