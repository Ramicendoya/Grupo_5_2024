from django.urls import path
from . import views
from django.utils import timezone
from django.views import View
from .views import GastoView,CategoriaView,EliminarGastoView,EditarIngresoView, CategoriaView, IngresoView, EliminarIngreso, ObtenerIngresoView,ReporteFinancieroView

urlpatterns = [
    path('', views.home, name='home'),


    #Gastos
    path('registrar/gasto/', GastoView.as_view(), name='registrar_gasto'),
    path('registrar/gasto/bajaGasto', EliminarGastoView.as_view(), name='baja_Gasto'),
    path('registrar/<str:origen>/cargarCategoria/', CategoriaView.as_view(), name='cargar_categoria'),
    

    # Registrar Ingresos
    path('registrar/ingreso/', IngresoView.as_view(), name='registrar_ingreso'),
    path('registrar/ingreso/<int:ingreso_pk>/eliminar', EliminarIngreso.as_view(), name='eliminar_ingreso'),
    path('registrar/<str:origen>/cargarCategoria/', CategoriaView.as_view(), name='cargar_categoria'),
    path('ingresos/obtener/<int:ingreso_pk>/', ObtenerIngresoView.as_view(), name='obtener_ingreso'),
    path('ingresos/editar/<int:ingreso_pk>/', EditarIngresoView.as_view(), name='editar_ingreso'),

    # Reporte Financiero
   path('ver/reporteFinanciero/<int:anio>/<int:mes>/', ReporteFinancieroView.as_view(), name='reporte_financiero'),
]