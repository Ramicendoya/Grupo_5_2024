from django.urls import path
from . import views
from .views import IngresoView, EliminarIngreso

urlpatterns = [
    path('', views.home, name='home'),
    path('gastos/', views.gastos, name='gastos'),


    # Registrar Ingresos
    path('registrar/ingreso/', IngresoView.as_view(), name='registrar_ingreso'),

    path('registrar/ingreso/<int:ingreso_pk>/eliminar', EliminarIngreso.as_view(), name='eliminar_ingreso'),

]