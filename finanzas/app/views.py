from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import Ingreso, Persona, Categoria,Recurrencia,Gasto, MovimientoIngreso, MovimientoGasto
from django.utils import timezone
from django.views import View
from django.db.models import Sum


def home(request):
    return render(request, 'home.html') 



class GastoView(View):
    def get(self, request):
        # Obtiene la lista de ingresos fijos y variables
        gastos_fijos = Gasto.objects.filter(bl_fijo=True,bl_baja=0)
        gastos_variables = Gasto.objects.filter(bl_fijo=False,bl_baja=0)
        categorias= Categoria.objects.filter(bl_baja=0)
        # Crea un contexto para pasar los ingresos a la plantilla
        context = {
            'gastos_fijos': gastos_fijos,
            'gastos_variables': gastos_variables,
            'categorias': categorias,
            'origen': 'gasto',
        }
        
        return render(request, 'gastos.html', context)
    
    def post(self, request):
        categoria_id = request.POST.get('categoria')
        

        gasto = Gasto(
            monto=request.POST.get('monto'),
            observaciones=request.POST.get('nombre_gasto'),
            persona=Persona.objects.first(),
            categoria = Categoria.objects.get(id=categoria_id),
            bl_fijo='tipo_gasto' in request.POST,
        )
        gasto.save()

        return redirect('registrar_gasto')
    


#    Ingresos:

class IngresoView(View):
    def get(self, request):
        # Obtengo la lista de ingresos fijos y variables, que no esten dados de baja
        ingresos_fijos = Ingreso.objects.filter(bl_fijo=True, bl_baja=False)
        ingresos_variables = Ingreso.objects.filter(bl_fijo=False, bl_baja=False)

    	# Obtengo la lista de categorias que no esten dadas de baja
        categorias = Categoria.objects.filter(bl_baja=False)
        
        # Creo un contexto para pasar los ingresos a la plantilla
        context = {
            'ingresos_fijos': ingresos_fijos,
            'ingresos_variables': ingresos_variables,
            'categorias': categorias,
            'origen': 'ingreso',
        }
        return render(request, 'ingresos.html', context)

    def post(self, request):
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        monto = request.POST.get('monto')
        fijo = 'tipo_ingreso' in request.POST
        categoria_id = request.POST.get('categoria') 
        categoria = get_object_or_404(Categoria, id=categoria_id)
        metodo_pago = request.POST.get('metodo_pago')

        persona = Persona.objects.first() 

        # Si es fijo, creo el ingreso, y la recurrencia, sino solo el ingreso
        if(fijo==True): 

            ingreso = Ingreso(
                nombre=nombre,
                persona=persona,
                fecha=timezone.now(), 
                monto=monto,
                descripcion=descripcion,
                bl_fijo=fijo,
                categoria = categoria,
                metodo_pago = metodo_pago,
            )

            ingreso.save() # Guardo el ingreso para poder obtener su pk y asignarselo a la recurrencia

            frecuencia = request.POST.get('frecuencia')
            
            # Convercion de la frecuencia a días
            if frecuencia == 'diario':
                dias = 1
            elif frecuencia == 'semanal':
                dias = 7
            elif frecuencia == 'mensual':
                dias = 30  # 
            elif frecuencia == 'anual':
                dias = 365
            elif frecuencia == 'personalizado':
                dias = int(request.POST.get('diasPersonalizados', 1))  # Por defecto a 1 si no se proporciona
            
            print(frecuencia)

            recurrencia=Recurrencia(
                fecha_desde=request.POST.get('fechaDesde'),
                fecha_hasta=request.POST.get('fechaHasta'),
                frecuencia=dias,
                ingreso=ingreso,
                gasto=None,
                bl_baja=False,
            )
            recurrencia.save()
   
        else:
            ingreso = Ingreso(
                nombre=nombre,
                persona=persona,
                fecha=timezone.now(), 
                monto=monto,
                descripcion=descripcion,
                bl_fijo=fijo,
                categoria = categoria,
                metodo_pago = metodo_pago,
            )
            ingreso.save()

        return redirect('registrar_ingreso')
    
class EliminarIngreso(View):
    def post(self, request, ingreso_pk):

        # Esto tenemos que reemplazarlo por la persona autenticada en la aplicacion
        persona = get_object_or_404(Persona, pk=1)
        
        # Busco el ingreso por la pk que se pasa en la URL
        ingreso = get_object_or_404(Ingreso, pk=ingreso_pk)

        # Verifico si el ingreso pertenece a la persona
        if ingreso.persona == persona:
            ingreso.bl_baja = True
            ingreso.save()

           # Si el ingreso es fijo, tambien elimino la recurrencia asociada
            if(ingreso.bl_fijo == True):
                recurrencias = Recurrencia.objects.filter(ingreso=ingreso)
                for recurrencia in recurrencias:
                    recurrencia.bl_baja = True
                    recurrencia.save()
            messages.success(request, "Ingreso eliminado con éxito.")
        else:
            messages.error(request, "El ingreso no pertenece a la persona especificada.")

        return redirect('registrar_ingreso')
    
class EditarIngresoView(View):
    def post(self, request, ingreso_pk):
        # Busco la persona
        persona = get_object_or_404(Persona, pk=1)  # esto hay que reemplazarlo por la persona autenticada en la aplicacion

        # Busca el ingreso por la pk que se pasa en la URL
        ingreso = get_object_or_404(Ingreso, pk=ingreso_pk)

        # Verifico si el ingreso pertenece a la persona
        if ingreso.persona != persona:
            messages.error(request, "No tienes permisos para editar este ingreso.")
            return redirect('registrar_ingreso')

        ingreso.nombre = request.POST.get('nombre')
        ingreso.descripcion = request.POST.get('descripcion')
        ingreso.monto = request.POST.get('monto')
        ingreso.bl_fijo = 'tipo_ingreso' in request.POST
        categoria_id = request.POST.get('categoria')
        print(categoria_id)
        ingreso.categoria = get_object_or_404(Categoria, id=categoria_id)
        ingreso.metodo_pago = request.POST.get('metodo_pago')

        ingreso.save()
        messages.success(request, "Ingreso actualizado con éxito.")
        return redirect('registrar_ingreso')
    
class ObtenerIngresoView(View):
    def get(self, request, ingreso_pk):
        # Busco la persona
        persona = get_object_or_404(Persona, pk=1) # esto hay que reemplazarlo por la persona autenticada en la aplicacion

        # Busco el ingreso por la pk que se pasa en la URL
        ingreso = get_object_or_404(Ingreso, pk=ingreso_pk)

        # Verifico si el ingreso pertenece a la persona
        if ingreso.persona == persona:
            ingreso_data = {
                'nombre': ingreso.nombre,
                'descripcion': ingreso.descripcion,
                'monto': ingreso.monto,
                'categoria_id': ingreso.categoria.id,
                'metodo_pago': ingreso.metodo_pago,
                'bl_fijo': ingreso.bl_fijo
            }
            return JsonResponse(ingreso_data)
        else:
            return JsonResponse({'error': 'Ingreso no pertenece a la persona autenticada'}, status=404)
    

class CategoriaView(View):

   def post(self, request,origen):        

        categoria = Categoria(
            nombre=request.POST.get('nombre_categoria'),
            detalle=request.POST.get('detalle'),
            persona=Persona.objects.first(), # esto hay que reemplazarlo por la persona autenticada en la aplicacion
            bl_general = 0,
        )
        categoria.save()

        # Redirige según el valor de origen
        if origen == 'gasto':
            return redirect('registrar_gasto')
        elif origen == 'ingreso':
            return redirect('registrar_ingreso')
        else:
            # Si el origen no es válido
            return redirect('home')

   
class EliminarGastoView(View):
    def post(self, request):        
        gasto = get_object_or_404(Gasto, id=request.POST.get('id_gasto'))
        
        # Modificamos el campo bl_baja del objeto existente
        gasto.bl_baja = 1
        gasto.save()

        # Redireccionamos a la vista de registrar_gasto
        return redirect('registrar_gasto')


class ObtenerSaldoActualView(View):
    def get(self, request):
        try:
            # Obtener la persona autenticada
            persona = get_object_or_404(Persona, pk=1)

            # Calcular los ingresos totales (filtrar movimientos activos)
            ingresos_total = Ingreso.objects.filter(
                persona=persona,
                bl_baja=0
            ).aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

            # Calcular los gastos totales (filtrar movimientos activos)
            gastos_total = Gasto.objects.filter(
                persona=persona,
                bl_baja=0
            ).aggregate(total_gastos=Sum('monto'))['total_gastos'] or 0

            # Calcular el saldo actual
            saldo_actual = ingresos_total - gastos_total

            # Retornar el saldo en un JsonResponse
            return JsonResponse({'saldo_actual': saldo_actual})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class ObtenerSaldoFuturoView(View):
    def get(self, request):
        try:
            persona_id = 1  # Asumimos que el ID de la persona es 1
            persona = get_object_or_404(Persona, pk=persona_id)

            # Obtener saldo actual
            ingresos_total = Ingreso.objects.filter(
                persona=persona,
                bl_baja=0
            ).aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

            gastos_total = Gasto.objects.filter(
                persona=persona,
                bl_baja=0
            ).aggregate(total_gastos=Sum('monto'))['total_gastos'] or 0

            saldo_actual = ingresos_total - gastos_total

            # Calcular saldo futuro
            saldo_futuro_1_mes = self.calcular_saldo_futuro(persona, 30, saldo_actual)
            saldo_futuro_2_meses = self.calcular_saldo_futuro(persona, 60, saldo_actual)
            saldo_futuro_3_meses = self.calcular_saldo_futuro(persona, 90, saldo_actual)

            return JsonResponse({
                'saldo_futuro_1_mes': saldo_futuro_1_mes,
                'saldo_futuro_2_meses': saldo_futuro_2_meses,
                'saldo_futuro_3_meses': saldo_futuro_3_meses
            })

        except Persona.DoesNotExist:
            return JsonResponse({'error': 'Persona no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def calcular_saldo_futuro(self, persona, dias, saldo_actual):
        ingresos_futuros_total = 0
        ingresos_fijos = Ingreso.objects.filter(
            persona=persona,
            bl_fijo=1,
            bl_baja=0
        )

        for ingreso in ingresos_fijos:
            recurrencias = Recurrencia.objects.filter(ingreso=ingreso, bl_baja=0)
            for recurrencia in recurrencias:
                repeticiones = dias // recurrencia.frecuencia
                ingresos_futuros_total += ingreso.monto * repeticiones

        gastos_futuros_total = 0
        gastos_fijos = Gasto.objects.filter(
            persona=persona,
            bl_fijo=1,
            bl_baja=0
        )

        for gasto in gastos_fijos:
            recurrencias = Recurrencia.objects.filter(gasto=gasto, bl_baja=0)
            for recurrencia in recurrencias:
                repeticiones = dias // recurrencia.frecuencia
                gastos_futuros_total += gasto.monto * repeticiones

        saldo_futuro = saldo_actual + ingresos_futuros_total - gastos_futuros_total
        return saldo_futuro