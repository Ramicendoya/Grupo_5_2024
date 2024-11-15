from django.urls import path
from . import views
from django.utils import timezone
from django.views import View
from .views import GastoView,CategoriaView,EliminarGastoView,EditarIngresoView, CategoriaView, Home, IngresoView, EliminarIngreso, ObtenerIngresoView , PromocionesView,ReporteFinancieroView,ObtenerSaldoActualView, ObtenerSaldoFuturoView, ObtenerGastoView, EditarGastoView,MovimientoGastoView, MetaView,ConfirmarYEditarGasto


urlpatterns = [
    
    # Home
    path('', Home.as_view(), name='home'),

    #Promociones
    path('promociones/', PromocionesView.as_view(), name='promociones'),
    # Gastos
    path('registrar/gasto/', GastoView.as_view(), name='registrar_gasto'),
    path('registrar/<str:origen>/cargarCategoria/', CategoriaView.as_view(), name='cargar_categoria'),
    path('gastos/eliminar/<int:gasto_pk>/', EliminarGastoView.as_view(), name='eliminar_gasto'),
    path('gastos/obtener/<int:gasto_pk>/', ObtenerGastoView.as_view(), name='obtener_gasto'),
    path('gastos/editar/<int:gasto_pk>/', EditarGastoView.as_view(), name='editar_gasto'),

    path('movimientos_gastos/<int:gasto_pk>/', MovimientoGastoView.as_view(), name='movimientos_gastos'),
    #path('movimientos_gastos/ConfirmarGasto/<int:gasto_pk>/', ConfirmarGasto.as_view(), name='confirmar_gasto'),
    path('confirmarYEditarGasto/<int:gasto_pk>/', ConfirmarYEditarGasto.as_view(), name='confirmarYEditargasto'),

    # Registrar Ingresos
    path('registrar/ingreso/', IngresoView.as_view(), name='registrar_ingreso'),
    path('registrar/ingreso/<int:ingreso_pk>/eliminar', EliminarIngreso.as_view(), name='eliminar_ingreso'),
    path('registrar/<str:origen>/cargarCategoria/', CategoriaView.as_view(), name='cargar_categoria'),
    path('ingresos/obtener/<int:ingreso_pk>/', ObtenerIngresoView.as_view(), name='obtener_ingreso'),
    path('ingresos/editar/<int:ingreso_pk>/', EditarIngresoView.as_view(), name='editar_ingreso'),

    # Reporte Financiero
    path('ver/reporteFinanciero/<str:tipo>/<int:anio>/<int:mes>/', ReporteFinancieroView.as_view(), name='reporte_financiero'),
    
    # Saldo Actual y Futuro
    path('saldo-actual/', ObtenerSaldoActualView.as_view(), name='saldo_actual'),
    path('saldo-futuro/', ObtenerSaldoFuturoView.as_view(), name='saldo_futuro'),


  # Metas
    path('metas/', MetaView.as_view(), name='metas'),  
]