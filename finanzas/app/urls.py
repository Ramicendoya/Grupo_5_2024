from django.urls import path
from . import views
from .views import IngresoView

urlpatterns = [
    path('', views.home, name='home'),
    path('gastos/', views.gastos, name='gastos'),


    # Registrar Ingresos
    path('registrar/ingreso/', IngresoView.as_view(), name='registrar_ingreso'),

    

]