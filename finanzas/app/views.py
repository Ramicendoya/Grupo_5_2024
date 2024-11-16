from datetime import date, timedelta
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .models import Ingreso, Persona, Categoria,Recurrencia,Gasto, MovimientoIngreso, MovimientoGasto,Meta
from django.utils import timezone
from django.views import View
from decimal import Decimal
#Se agergo desde aca 13112024 en la facu
from django.db import connection
#Se agergo hasta aca 13112024 en la facu

class Home(View):
    def get(self, request):
        # Busco la persona
        persona = get_object_or_404(Persona, pk=1)
             
        # Obtiene la lista de gastos
        gastos = Gasto.objects.filter(persona=persona, bl_baja=0)

        # Calculo el monto total de gastos
        total_global_gastos = gastos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        # Inicializa categorias como un QuerySet vacío
        categorias = Categoria.objects.none()  
        hay_resultados = False  # Inicializa la variable de resultados

        # Verifico si hay gastos para calcular los porcentajes
        if total_global_gastos > 0:
            hay_resultados = True

            # Filtro y calculo total de gastos por categoría y porcentaje
            gastos_por_categoria = (
                gastos
                .values('categoria__nombre')
                .annotate(
                    total=Sum('monto'),
                    porcentaje=(Sum('monto') * Decimal('100.0') / total_global_gastos)
                )
            )
            # Obtengo los nombres de las categorías que tienen gastos
            categorias_de_gastos = [gasto['categoria__nombre'] for gasto in gastos_por_categoria]

            # Creo un QuerySet que obtenga directamente las categorías de gastos
            if categorias_de_gastos:
                categorias = Categoria.objects.filter(nombre__in=categorias_de_gastos, bl_baja=False)

        # Si no hay gastos, asigno un QuerySet vacío
        else:
            gastos_por_categoria = []

        # Obtiene la lista de ingresos
        ingresos = Ingreso.objects.filter(persona=persona, bl_baja=0)

        # Calculo el monto total de ingresos
        total_global_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        # Verifico si hay ingresos para calcular los porcentajes
        if total_global_ingresos > 0:
            hay_resultados = True  # Si hay ingresos, mantengo la variable

            # Filtro y calculo total de ingresos por categoría y porcentaje
            ingresos_por_categoria = (
                ingresos
                .values('categoria__nombre')
                .annotate(
                    total=Sum('monto'),
                    porcentaje=(Sum('monto') * Decimal('100.0') / total_global_ingresos)
                )
            )
            # Obtengo los nombres de las categorías que tienen ingresos
            categorias_de_ingresos = [ingreso['categoria__nombre'] for ingreso in ingresos_por_categoria]

            # Creo un QuerySet que obtenga directamente las categorías de ingresos
            if categorias_de_ingresos:
                categorias = categorias | Categoria.objects.filter(nombre__in=categorias_de_ingresos, bl_baja=False)

        # Si no hay ingresos, asigno un QuerySet vacío
        else:
            ingresos_por_categoria = []


        # Metas
        
        # metas = Meta.objects.all()
        
        # Cuentar metas cumplidas y no cumplidas
        metas_cumplidas = 7 # metas.filter(cumplida=True).count()
        metas_totales = 10 # metas.count()
        metas_no_cumplidas = metas_totales - metas_cumplidas if metas_totales else 0

        # Creo el contexto para pasarlo al template
        context = {
            'gastos': list(gastos.values('id', 'nombre', 'observaciones', 'monto', 'fecha', 'categoria__nombre')),
            'ingresos': list(ingresos.values('id', 'nombre','descripcion', 'monto', 'fecha', 'categoria__nombre')),
            'categorias': list(categorias.values()),  
            'gastos_por_categoria': list(gastos_por_categoria),
            'ingresos_por_categoria': list(ingresos_por_categoria),
            'hay_resultados': hay_resultados,
            'metas_cumplidas': metas_cumplidas,
            'metas_totales': metas_totales,
            'metas_no_cumplidas': metas_no_cumplidas,
        }

        # Función para serializar objetos que no son JSON serializables
        def serialize_value(value):
            if isinstance(value, Decimal):
                return float(value)  # Convierte Decimal a float
            if isinstance(value, date):
                return value.isoformat()  # Convierte date a cadena en formato ISO
            return value  # Retorna el valor tal como está

        # Serializa los valores del contexto
        for key in context:
            if isinstance(context[key], list):
                for item in context[key]:
                    for k, v in item.items():
                        item[k] = serialize_value(v)

        # Convierte el contexto a JSON
        context_json = json.dumps(context)
#Se agergo desde aca 13112024 en la facu
        with connection.cursor() as cursor:
            # Ejecuta la consulta sobre la vista
            cursor.execute("SELECT * FROM gastos_pendientes")
            # Obtiene todos los resultados
            resultados = cursor.fetchall()

            cursor.execute("SELECT * FROM ingresos_pendientes")
            # Obtiene todos los resultados
            resultados_ingreso = cursor.fetchall()

        # Procesa los resultados (opcional)
        gastos_pendientes = []
        ingresos_pendientes = []
        for fila in resultados:
            gastos_pendientes.append({
                'id_categoria': fila[0],
                'categoria': fila[1],
                'id_gasto': fila[2],
                'nombre': fila[3],
                'monto': fila[4]
            })
        #Agregado el 15/11/2024
        for fila_ingreso in resultados_ingreso:
            ingresos_pendientes.append({
                'id_categoria': fila_ingreso[0],
                'categoria': fila_ingreso[1],
                'id_ingreso': fila_ingreso[2],
                'nombre': fila_ingreso[3],
                'monto': fila_ingreso[4]
            })
        #Agregado hasta aca el 15/11/2024
        print(ingresos_pendientes)
        #Ya esta terminado. falta que se agregue en el acordeon lo que devuelve gastos y agregarle un boton que ese boton sea pagar o modificar y pagar
        #Se agergo hasta aca 13112024 en la facu
        return render(request, 'home.html', {'context': context_json,'gastos_pendientes':gastos_pendientes,'ingresos_pendientes':ingresos_pendientes})

class PromocionesView(View):
    def get(self, request):

        return render(request, 'promociones.html')


class GastoView(View):
    def get(self, request):
        # Obtiene la lista de Gasto fijos y variables
        gastos_fijos = Gasto.objects.filter(bl_fijo=True,bl_baja=0)
        gastos_variables = Gasto.objects.filter(bl_fijo=False,bl_baja=0)
        categorias= Categoria.objects.filter(bl_baja=0)
        # Crea un contexto para pasar los Gasto a la plantilla
        context = {
            'gastos_fijos': gastos_fijos,
            'gastos_variables': gastos_variables,
            'categorias': categorias,
            'origen': 'gasto',
        }
        
        return render(request, 'gastos.html', context)
    
    def post(self, request):
        #parametros_post = request.POST.dict()
        #return JsonResponse(parametros_post)
        categoria_id = request.POST.get('categoria')
        bl_fijo='tipo_gasto' in request.POST
        if(bl_fijo==True): 
            gasto = Gasto(
                monto=request.POST.get('monto'),
                observaciones=request.POST.get('nombre_gasto'),
                persona=Persona.objects.first(),
                categoria = Categoria.objects.get(id=categoria_id),
                metodo_pago=(request.POST.get('metodo_pago')).capitalize(),
                fecha = timezone.now().date(),
                bl_fijo='tipo_gasto' in request.POST,
            )
            #Se agergo desde aca 13112024 en la facu
            gasto.save()
            movimientogasto=MovimientoGasto(
                monto=request.POST.get('monto'),
                fecha = timezone.now().date(),
                bl_baja=0,
                gasto=gasto,
            )
            movimientogasto.save()
            #Se agergo hasta aca 13112024 en la facu
            frecuencia = request.POST.get('frecuencia')

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

            recurrencia=Recurrencia(
                    fecha_desde=request.POST.get('fechaDesde'),
                    fecha_hasta=request.POST.get('fechaHasta'),
                    frecuencia=dias,
                    gasto=gasto,
                    ingreso=None,
                    bl_baja=False,
                )
            recurrencia.save()
        else:
            gasto = Gasto(
                monto=request.POST.get('monto'),
                observaciones=request.POST.get('nombre_gasto'),
                persona=Persona.objects.first(),
                categoria = Categoria.objects.get(id=categoria_id),
                metodo_pago=(request.POST.get('metodo_pago')).capitalize(),
                fecha = timezone.now().date(),
                bl_fijo='tipo_gasto' in request.POST,
            )
            gasto.save()
            #Se agergo desde aca 13112024 en la facu
            movimientogasto=MovimientoGasto(
                monto=request.POST.get('monto'),
                fecha = timezone.now().date(),
                bl_baja=0,
                gasto=gasto,
            )
            movimientogasto.save
            #Se agergo hasta aca 13112024 en la facu
        return redirect('registrar_gasto')
    
class ObtenerGastoView(View):
    def get(self, request, gasto_pk):
            # Busco la persona
            persona = get_object_or_404(Persona, pk=1) # esto hay que reemplazarlo por la persona autenticada en la aplicacion

            # Busco el Gasto por la pk que se pasa en la URL
            gasto = get_object_or_404(Gasto, pk=gasto_pk)

            # Verifico si el Gasto pertenece a la persona
            if gasto.persona == persona:
                gasto_data = {
                    'nombre': gasto.observaciones,
                    'monto': gasto.monto,
                    'categoria_id': gasto.categoria.id,
                    'metodo_pago': gasto.metodo_pago,
                    'bl_fijo': gasto.bl_fijo
                    
                }
                print(gasto_data)
                return JsonResponse(gasto_data)
            else:
                return JsonResponse({'error': 'Gasto no pertenece a la persona autenticada'}, status=404)

class EditarGastoView(View):
     def post(self, request, gasto_pk):
        #parametros_post = request.POST.dict()
        #return JsonResponse(parametros_post)
        persona = get_object_or_404(Persona, pk=1)  # esto hay que reemplazarlo por la persona autenticada en la aplicacion

        
        # Busca el Gasto por la pk que se pasa en la URL
        gasto = get_object_or_404(Gasto, pk=gasto_pk)

        if gasto.persona != persona:
            messages.error(request, "No tienes permisos para editar este gasto.")
            return redirect('registrar_gasto')

        gasto.observaciones = request.POST.get('nombre')
        #gasto.descripcion = request.POST.get('descripcion')
        gasto.monto = request.POST.get('monto')
        gasto.bl_fijo = 'tipo_gastoModal' in request.POST
        categoria_id = request.POST.get('categoria')
        print(categoria_id)
        gasto.categoria = get_object_or_404(Categoria, id=categoria_id)
        gasto.metodo_pago = request.POST.get('metodo_pago')
        gasto.fecha=timezone.now().date()
        gasto.save()
        #Se agergo desde aca 13112024 en la facu
       # movimientogasto=MovimientoGasto(
       #    monto=request.POST.get('monto'),
       #     fecha = timezone.now().date(),
       #     bl_baja=0,
       #    gasto=gasto,
       # )
       #movimientogasto.save()
        #Se agergo hasta aca 13112024 en la facu
        messages.success(request, "Gasto actualizado con éxito.")
        return redirect('registrar_gasto')
     
   
class EliminarGastoView(View):
    def post(self, request, gasto_pk):
        #print(gasto_pk)
        #parametros_post = request.POST.dict()
        #return JsonResponse(parametros_post)
        # Esto tenemos que reemplazarlo por la persona autenticada en la aplicacion
        persona = get_object_or_404(Persona, pk=1)
        
        # Busco el ingreso por la pk que se pasa en la URL
        gasto = get_object_or_404(Gasto, pk=gasto_pk)
        
        # Verifico si el ingreso pertenece a la persona
        if gasto.persona == persona:
            gasto.bl_baja = True
            gasto.save()

           # Si el ingreso es fijo, tambien elimino la recurrencia asociada
            if(gasto.bl_fijo == True):
                recurrencias = Recurrencia.objects.filter(gasto=gasto)
                for recurrencia in recurrencias:
                    recurrencia.bl_baja = True
                    recurrencia.save()
            messages.success(request, "Gasto eliminado con éxito.")
        else:
            messages.error(request, "El Gasto no pertenece a la persona especificada.")

        return redirect('registrar_gasto')

class MovimientoGastoView(View):
    def get(self, request, gasto_pk):
          # Busco la persona
            persona = get_object_or_404(Persona, pk=1) # esto hay que reemplazarlo por la persona autenticada en la aplicacion

            # Busco el Gasto por la pk que se pasa en la URL
            gasto = get_object_or_404(Gasto, pk=gasto_pk)
            movimientos_gastos =  MovimientoGasto.objects.filter(gasto=gasto,bl_baja=0)
    
            # Verifico si el Gasto pertenece a la persona
            if gasto.persona == persona:
                if not movimientos_gastos:
                    return JsonResponse({'movimientos_gastos': []})

                movimientos_data = []
                for movimiento in movimientos_gastos:
                    movimientos_data.append({
                    'categoria': movimiento.gasto.categoria.nombre,
                    'descripcion': movimiento.gasto.observaciones,
                    'metodo_pago':movimiento.gasto.metodo_pago,
                    'monto': movimiento.monto,
                    'fecha': movimiento.fecha.strftime('%Y-%m-%d')  # Formateamos la fecha
                })
                print(movimientos_data)
                return JsonResponse({'movimientos_gastos': movimientos_data})
            else:
                return JsonResponse({'error': 'Gasto no pertenece a la persona autenticada'}, status=404)

class ConfirmarYEditarGasto(View):
    def post(self, request, gasto_pk):
        print("entro")
        # Busco la persona
        persona = get_object_or_404(Persona, pk=1) # esto hay que reemplazarlo por la persona autenticada en la aplicacion

        # Busco el Gasto por la pk que se pasa en la URL
        gasto = get_object_or_404(Gasto, pk=gasto_pk)

        if gasto.persona == persona:
            gasto.monto = request.POST.get('monto')
            gasto.save()
            movimientogasto=MovimientoGasto(
            monto=request.POST.get('monto'),
            fecha = timezone.now().date(),
            bl_baja=0,
            gasto=gasto,
            )
            movimientogasto.save()
            
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)    
                

            else:
                return JsonResponse({'error': 'Gasto no pertenece a la persona autenticada'}, status=404)
        
#Se agrego el 15/11/2024 16:39
class ConfirmarGasto(View):
    def post(self, request, gasto_pk):
        # Busco la persona
           persona = get_object_or_404(Persona, pk=1) # esto hay que reemplazarlo por la persona autenticada en la aplicacion

            # Busco el Gasto por la pk que se pasa en la URL
           gasto = get_object_or_404(Gasto, pk=gasto_pk)
           print(gasto)
           if gasto.persona == persona:

                movimientogasto=MovimientoGasto(
                    monto=gasto.monto,
                    fecha = timezone.now().date(),
                    bl_baja=0,
                    gasto=gasto,
                )
                movimientogasto.save()
                referer = request.META.get('HTTP_REFERER')
                if referer:
                    return redirect(referer) 
           else:
                return JsonResponse({'error': 'Gasto no pertenece a la persona autenticada'}, status=404)
           
#Se agrego el 15/11/2024 16:39
#    Ingresos:
####################################################################################################
####################################################################################################
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

            # Creo el movimiento, le asocio el ingreso y lo persisto
            movimiento = MovimientoIngreso(
                monto = monto,
                fecha = timezone.now(),
                ingreso = ingreso,
            )

            movimiento.save()

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

            # Creo el movimiento, le asocio el ingreso y lo persisto
            movimiento = MovimientoIngreso(
                monto = monto,
                fecha = timezone.now(),
                ingreso = ingreso,
            )
            movimiento.save()

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



####################################################################################################
####################################################################################################
#  Reporte Financiero
####################################################################################################
####################################################################################################

class ReporteFinancieroView(View):
    def get(self, request, tipo, anio=None, mes=None):
        # Busco la persona
        persona = get_object_or_404(Persona, pk=1)

        if tipo == 'ingresos':
            context = self.obtener_ingresos(persona, anio, mes)
        elif tipo == 'gastos':
            context = self.obtener_gastos(persona, anio, mes)
        else:
            # Si el tipo no es válido
            error = "Tipo de reporte no válido"
            context = {
                'error': error,
            }
            return render(request, 'reporte_financiero.html', {'context': context})

        # Función para serializar objetos que no son JSON serializables
        def serialize_value(value):
            if isinstance(value, Decimal):
                return float(value)  # Convierte Decimal a float
            if isinstance(value, date):
                return value.isoformat()  # Convierte date a cadena en formato ISO
            return value  # Retorna el valor tal como está

        # Serializa los valores del contexto
        for key in context:
            if isinstance(context[key], list):
                for item in context[key]:
                    for k, v in item.items():
                        item[k] = serialize_value(v)

        # Convierte el contexto a JSON
        context_json = json.dumps(context)
        return render(request, 'reporte_financiero.html', {'context': context_json})

    def obtener_ingresos(self, persona, anio, mes):
        # Obtengo la lista de ingresos que no estén dados de baja
        ingresos = Ingreso.objects.filter(bl_baja=False, persona=persona)

        # Filtrar por año si se seleccionó uno
        if anio:
            ingresos = ingresos.filter(fecha__year=anio)

        # Filtrar por mes si se seleccionó uno
        if mes > 0 and mes <= 12:
            ingresos = ingresos.filter(fecha__month=mes)
        elif mes != 0:
            # Si mes es distinto de cero, significa que no se seleccionó ni "Reporte Anual" (mes=0) ni ningun mes correcto
            return {"error": "Mes incorrecto"}

        # Calculo el monto total de ingresos
        total_global = ingresos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        # Inicializa categorias como un QuerySet vacío
        categorias = Categoria.objects.none()

        # Verifico si hay ingresos para calcular los porcentajes
        if total_global > 0:
            hay_resultados = True

            # Filtro y calculo total de ingresos por categoría y porcentaje
            ingresos_por_categoria = (
                ingresos
                .values('categoria__nombre')
                .annotate(
                    total=Sum('monto'),
                    porcentaje=(Sum('monto') * Decimal('100.0') / total_global)
                )
            )
            # Obtengo los nombres de las categorías que tienen ingresos
            categorias_de_ingresos = [ingreso['categoria__nombre'] for ingreso in ingresos_por_categoria]

            # Crear un QuerySet que obtenga directamente las categorías de ingresos
            if categorias_de_ingresos:
                categorias = Categoria.objects.filter(nombre__in=categorias_de_ingresos, bl_baja=False)

        # Si no hay ingresos, asigno un QuerySet vacío
        else:
            ingresos_por_categoria = []
            hay_resultados = False 

        # Creo el contexto para pasarlo al template
        context = {
            'ingresos': list(ingresos.values('id', 'nombre','descripcion', 'monto', 'fecha', 'categoria__nombre')),
            'gastos': [],
            'categorias': list(categorias.values()),  
            'ingresos_por_categoria': list(ingresos_por_categoria),
            'hay_resultados': hay_resultados,
        }
        return context

    def obtener_gastos(self, persona, anio, mes):
        # Obtengo la lista de gastos que no estén dados de baja
        gastos = Gasto.objects.filter(bl_baja=False, persona=persona)

        # Filtrar por año si se seleccionó uno
        if anio:
            gastos = gastos.filter(fecha__year=anio)

        # Filtrar por mes si se seleccionó uno
        if mes > 0 and mes <= 12:
            gastos = gastos.filter(fecha__month=mes)
        elif mes != 0:
            # Si mes es distinto de cero, significa que no se seleccionó ni "Reporte Anual" (mes=0) ni ningun mes correcto
            return {"error": "Mes incorrecto"}

        # Calculo el monto total de gastos
        total_global = gastos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        # Inicializa categorias como un QuerySet vacío
        categorias = Categoria.objects.none()  

        # Verifico si hay gastos para calcular los porcentajes
        if total_global > 0:
            hay_resultados = True

            # Filtro y calculo total de gastos por categoría y porcentaje
            gastos_por_categoria = (
                gastos
                .values('categoria__nombre')
                .annotate(
                    total=Sum('monto'),
                    porcentaje=(Sum('monto') * Decimal('100.0') / total_global)
                )
            )
            # Obtengo los nombres de las categorías que tienen gastos
            categorias_de_gastos = [gasto['categoria__nombre'] for gasto in gastos_por_categoria]

            # Crear un QuerySet que obtenga directamente las categorías de gastos
            if categorias_de_gastos:
                categorias = Categoria.objects.filter(nombre__in=categorias_de_gastos, bl_baja=False)

        # Si no hay gastos, asigno un QuerySet vacío
        else:
            gastos_por_categoria = []
            hay_resultados = False 

        # Creo el contexto para pasarlo al template
        context = {
            'gastos': list(gastos.values('id', 'nombre','observaciones', 'monto', 'fecha', 'categoria__nombre')),
            'ingresos': [],
            'categorias': list(categorias.values()),  
            'gastos_por_categoria': list(gastos_por_categoria),
            'hay_resultados': hay_resultados,
        }
        return context



####################################################################################################
####################################################################################################
# Obtener Saldo Actual y Futuro
####################################################################################################
####################################################################################################

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
    

####################################################################################################
####################################################################################################
# Historico de saldos
####################################################################################################
####################################################################################################

class ObtenerHistoricoSaldoView(View):
    def get(self, request):
        try:
            persona = get_object_or_404(Persona, pk=1)

            # Obtener el saldo actual y el historial de saldos
            saldo_actual = self.calcular_saldo_actual(persona)
            historial_saldos = self.calcular_historial_saldos(persona, saldo_actual)
            
            return JsonResponse({'historial_saldos': historial_saldos})

        except Persona.DoesNotExist:
            return JsonResponse({'error': 'Persona no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def calcular_saldo_actual(self, persona):
        """Calcula el saldo actual sumando ingresos y restando gastos."""
        ingresos_total = Ingreso.objects.filter(
            persona=persona,
            bl_baja=0
        ).aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

        gastos_total = Gasto.objects.filter(
            persona=persona,
            bl_baja=0
        ).aggregate(total_gastos=Sum('monto'))['total_gastos'] or 0

        return ingresos_total - gastos_total

    def calcular_historial_saldos(self, persona, saldo_actual):
        """Calcula el saldo histórico mes a mes, incluyendo proyecciones futuras."""
        historial_saldos = []
        fecha_actual = timezone.now().date()

        # Calcular saldo para cada mes en el último año
        for mes in range(0, 12):
            fecha_inicio_mes = fecha_actual - timedelta(days=30 * mes)
            
            # Inicializa el saldo del mes
            ingresos_mes = Ingreso.objects.filter(
                persona=persona,
                bl_baja=0,
                fecha__year=fecha_inicio_mes.year,
                fecha__month=fecha_inicio_mes.month
            ).aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

            gastos_mes = Gasto.objects.filter(
                persona=persona,
                bl_baja=0,
                fecha__year=fecha_inicio_mes.year,
                fecha__month=fecha_inicio_mes.month
            ).aggregate(total_gastos=Sum('monto'))['total_gastos'] or 0

            # Calcula el saldo del mes, asegurando que sea cero si no hay movimientos
            saldo_mes = ingresos_mes - gastos_mes  # Calculamos el saldo del mes
            historial_saldos.insert(0, {
                'fecha': fecha_inicio_mes.isoformat(),  # Formato ISO (YYYY-MM-DD)
                'saldo': saldo_mes  # Se mostrará cero si no hay ingresos ni gastos
            })

        # Proyección para los próximos 3 meses
        for i in range(1, 4):
            saldo_futuro = self.calcular_saldo_futuro(persona, 30 * i, saldo_actual)
            futuro_fecha = fecha_actual + timedelta(days=30 * i)  # Fecha futura
            historial_saldos.append({
                'fecha': futuro_fecha.isoformat(),  # Formato ISO (YYYY-MM-DD)
                'saldo': saldo_futuro
            })

        return historial_saldos


    def calcular_saldo_futuro(self, persona, dias, saldo_actual):
        """Proyecta el saldo futuro en función de ingresos y gastos recurrentes."""
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
    

####################################################################################################
####################################################################################################
# Historico de saldos
####################################################################################################
####################################################################################################

class ObtenerHistoricoSaldoView(View):
    def get(self, request):
        try:
            persona = get_object_or_404(Persona, pk=1)

            # Obtener el saldo actual y el historial de saldos
            saldo_actual = self.calcular_saldo_actual(persona)
            historial_saldos = self.calcular_historial_saldos(persona, saldo_actual)
            
            return JsonResponse({'historial_saldos': historial_saldos})

        except Persona.DoesNotExist:
            return JsonResponse({'error': 'Persona no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def calcular_saldo_actual(self, persona):
        """Calcula el saldo actual sumando ingresos y restando gastos."""
        ingresos_total = Ingreso.objects.filter(
            persona=persona,
            bl_baja=0
        ).aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

        gastos_total = Gasto.objects.filter(
            persona=persona,
            bl_baja=0
        ).aggregate(total_gastos=Sum('monto'))['total_gastos'] or 0

        return ingresos_total - gastos_total

    def calcular_historial_saldos(self, persona, saldo_actual):
        """Calcula el saldo histórico mes a mes, incluyendo proyecciones futuras."""
        historial_saldos = []
        fecha_actual = timezone.now().date()

        # Calcular saldo para cada mes en el último año
        for mes in range(0, 12):
            fecha_inicio_mes = fecha_actual - timedelta(days=30 * mes)
            
            # Inicializa el saldo del mes
            ingresos_mes = Ingreso.objects.filter(
                persona=persona,
                bl_baja=0,
                fecha__year=fecha_inicio_mes.year,
                fecha__month=fecha_inicio_mes.month
            ).aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

            gastos_mes = Gasto.objects.filter(
                persona=persona,
                bl_baja=0,
                fecha__year=fecha_inicio_mes.year,
                fecha__month=fecha_inicio_mes.month
            ).aggregate(total_gastos=Sum('monto'))['total_gastos'] or 0

            # Calcula el saldo del mes, asegurando que sea cero si no hay movimientos
            saldo_mes = ingresos_mes - gastos_mes  # Calculamos el saldo del mes
            historial_saldos.insert(0, {
                'fecha': fecha_inicio_mes.isoformat(),  # Formato ISO (YYYY-MM-DD)
                'saldo': saldo_mes  # Se mostrará cero si no hay ingresos ni gastos
            })

        # Proyección para los próximos 3 meses
        for i in range(1, 4):
            saldo_futuro = self.calcular_saldo_futuro(persona, 30 * i, saldo_actual)
            futuro_fecha = fecha_actual + timedelta(days=30 * i)  # Fecha futura
            historial_saldos.append({
                'fecha': futuro_fecha.isoformat(),  # Formato ISO (YYYY-MM-DD)
                'saldo': saldo_futuro
            })

        return historial_saldos


    def calcular_saldo_futuro(self, persona, dias, saldo_actual):
        """Proyecta el saldo futuro en función de ingresos y gastos recurrentes."""
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


#Meta 

class MetaView(View):
    def get(self, request):
        metas = Meta.objects.filter(bl_baja=False)
        
        context = {
            'metas': metas,
        }
        
        return render(request, 'metas.html', context)

    def post(self, request):
        # Obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        valor_meta = request.POST.get('valor_meta')
        ahorrado = request.POST.get('ahorrado')
        fecha_deseada = request.POST.get('fecha_deseada')
        descripcion = request.POST.get('descripcion')

        meta = Meta(
            nombre=nombre,
            valor_meta=valor_meta,
            ahorrado=ahorrado,
            fecha_deseada=fecha_deseada,
            descripcion=descripcion,
            bl_baja=False, 
        )
        meta.save()
        return redirect('metas') 
        
     
    def metas_grafico(request):

        # Filtramos las metas que no estan marcadas como baja
        total_metas = Meta.objects.filter(bl_baja=False)
        
        # Filtra las metas donde el valor ahorrado es mayor o igual (gte) al valor de la meta
        metas_cumplidas = total_metas.filter(ahorrado__gte=F('valor_meta')).count()
        
        # Filtra las metas donde el valor ahorrado es menor (lt) al valor de la meta
        metas_no_cumplidas = total_metas.filter(ahorrado__lt=F('valor_meta')).count()

        return JsonResponse({
            'metas_cumplidas': metas_cumplidas,
            'metas_no_cumplidas': metas_no_cumplidas
        })