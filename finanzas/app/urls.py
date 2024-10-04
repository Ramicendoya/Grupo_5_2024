from django.urls import path
from . import views
from .views import EditarIngresoView, CategoriaView, IngresoView, EliminarIngreso, ObtenerIngresoView

urlpatterns = [
    path('', views.home, name='home'),
    path('gastos/', views.gastos, name='registrar_gasto'),


    # Registrar Ingresos
    path('registrar/ingreso/', IngresoView.as_view(), name='registrar_ingreso'),
    path('registrar/ingreso/<int:ingreso_pk>/eliminar', EliminarIngreso.as_view(), name='eliminar_ingreso'),
    path('registrar/ingreso/cargarCategoria', CategoriaView.as_view(), name='cargar_categoria'),
    path('ingresos/obtener/<int:ingreso_pk>/', ObtenerIngresoView.as_view(), name='obtener_ingreso'),
    path('ingresos/editar/<int:ingreso_pk>/', EditarIngresoView.as_view(), name='editar_ingreso'),


     
    
]