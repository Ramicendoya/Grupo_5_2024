from django.urls import path
from . import views
from django.utils import timezone
from django.views import View
from .views import AhorroView,Calcular_meses_restantes,GastoView,CategoriaView,EliminarGastoView,EditarIngresoView, CategoriaView, Home, IngresoView, EliminarIngreso, ObtenerIngresoView , PromocionesView,ReporteFinancieroView,ObtenerSaldoActualView, ObtenerSaldoFuturoView, ObtenerHistoricoSaldoView, ObtenerGastoView, EditarGastoView,MovimientoGastoView, MetaView,ConfirmarYEditarGasto,ConfirmarGasto, ConfirmarIngreso, ConfirmarYEditarIngreso,MovimientoIngresoView, ObtenerAhorroEIngresosFijosView



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

    path('confirmarGasto/<int:gasto_pk>/', ConfirmarGasto.as_view(), name='confirmar_gasto'),
    path('confirmarYEditarGasto/<int:gasto_pk>/', ConfirmarYEditarGasto.as_view(), name='confirmarYEditargasto'),

    # Registrar Ingresos
    path('registrar/ingreso/', IngresoView.as_view(), name='registrar_ingreso'),
    path('registrar/ingreso/<int:ingreso_pk>/eliminar', EliminarIngreso.as_view(), name='eliminar_ingreso'),
    path('registrar/<str:origen>/cargarCategoria/', CategoriaView.as_view(), name='cargar_categoria'),
    path('ingresos/obtener/<int:ingreso_pk>/', ObtenerIngresoView.as_view(), name='obtener_ingreso'),
    path('ingresos/editar/<int:ingreso_pk>/', EditarIngresoView.as_view(), name='editar_ingreso'),

    path('movimientos_ingresos/ConfirmarIngreso/<int:ingreso_pk>/', ConfirmarIngreso.as_view(), name='confirmar_ingreso'),
    path('confirmarYEditarIngreso/<int:ingreso_pk>/', ConfirmarYEditarIngreso.as_view(), name='confirmarYEditaringreso'),
    path('movimientos_ingresos/<int:ingreso_pk>/', MovimientoIngresoView.as_view(), name='movimientos_ingresos'),
    # Reporte Financiero
    path('ver/reporteFinanciero/<str:tipo>/<int:anio>/<int:mes>/', ReporteFinancieroView.as_view(), name='reporte_financiero'),
    
    # Saldo Actual y Futuro
    path('saldo-actual/', ObtenerSaldoActualView.as_view(), name='saldo_actual'),
    path('saldo-futuro/', ObtenerSaldoFuturoView.as_view(), name='saldo_futuro'),
    path('api/ahorro-ingresos-fijos/', ObtenerAhorroEIngresosFijosView.as_view(), name='ahorro_ingresos_fijos'),

    # Historico de saldos
    path('saldos-historicos/', ObtenerHistoricoSaldoView.as_view(), name='saldos-historicos'),

    # Metas
    path('metas/', MetaView.as_view(), name='metas'),
    path('metas/grafico/', MetaView.metas_grafico, name='metas_grafico'),

    path('ahorro/', AhorroView.as_view(), name='ahorro'),


  # Metas
    path('metas/', MetaView.as_view(), name='metas'),  
    path('calcular_meses_restantes/', Calcular_meses_restantes.as_view(), name='calcular_meses_restantes'),  
]