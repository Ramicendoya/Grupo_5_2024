from datetime import date
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Sum
from .models import Ingreso, Persona, Categoria,Recurrencia,Gasto
from django.utils import timezone
from django.views import View
from decimal import Decimal


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



####################################################################################################
####################################################################################################
#  Reporte Financiero
####################################################################################################
####################################################################################################

class ReporteFinancieroView(View):
    def get(self, request, tipo, anio=None, mes=None):
        # Busco la persona (reemplaza esto por la persona autenticada en la aplicación)
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
            'ingresos': list(ingresos.values()),
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
            'gastos': list(gastos.values()),
            'ingresos': [],
            'categorias': list(categorias.values()),  
            'gastos_por_categoria': list(gastos_por_categoria),
            'hay_resultados': hay_resultados,
        }
        return context




