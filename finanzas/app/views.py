from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import Persona, Categoria,Gasto
from django.utils import timezone
from django.views import View

# Create your views here.

def home(request):
    return render(request, 'home.html') 

def ingresos(request):
    return render(request, 'ingresos.html') 

def gastos(request):
    return render(request, 'gastos.html') 


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
            'categorias': categorias
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
    
class CategoriaView(View):

   def post(self, request):        

        categoria = Categoria(
            nombre=request.POST.get('nombre_categoria'),
            detalle=request.POST.get('detalle'),
            persona=Persona.objects.first(),
            bl_general = 0,
        )
        categoria.save()

        return redirect('registrar_gasto')
   
class EliminarGastoView(View):
    def post(self, request):        
        gasto = get_object_or_404(Gasto, id=request.POST.get('id_gasto'))
        
        # Modificamos el campo bl_baja del objeto existente
        gasto.bl_baja = 1
        gasto.save()

        # Redireccionamos a la vista de registrar_gasto
        return redirect('registrar_gasto')