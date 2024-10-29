from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import Ingreso, Persona, Categoria,Recurrencia,Gasto
from django.utils import timezone
from django.views import View


def home(request):
    return render(request, 'home.html') 



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
                metodo_pago=request.POST.get('metodo_pago'),
                fecha = timezone.now().date(),
                bl_fijo='tipo_gasto' in request.POST,
            )
            
            gasto.save()

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
                metodo_pago=request.POST.get('metodo_pago'),
                fecha = timezone.now().date(),
                bl_fijo='tipo_gasto' in request.POST,
            )
            gasto.save()
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

        gasto.save()
        messages.success(request, "Gasto actualizado con éxito.")
        return redirect('registrar_gasto')
     
   
class EliminarGastoView(View):
    def post(self, request, gasto_pk):
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

