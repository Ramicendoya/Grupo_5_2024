from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import Ingreso, Persona, Categoria
from django.utils import timezone
from django.views import View


def home(request):
    return render(request, 'home.html') 

def gastos(request):
    return render(request, 'gastos.html')



#    Ingresos:

class IngresoView(View):
    def get(self, request):
        # Obtiene la lista de ingresos fijos y variables
        ingresos_fijos = Ingreso.objects.filter(fijo=True)
        ingresos_variables = Ingreso.objects.filter(fijo=False)
        
        # Crea un contexto para pasar los ingresos a la plantilla
        context = {
            'ingresos_fijos': ingresos_fijos,
            'ingresos_variables': ingresos_variables,
        }
        return render(request, 'ingresos.html', context)

    def post(self, request):

        descripcion = request.POST.get('descripcion')
        monto = request.POST.get('monto')
        fijo = 'tipo_ingreso' in request.POST

        persona = Persona.objects.first() 

        ingreso = Ingreso(
            persona=persona,
            fecha=timezone.now(), 
            monto=monto,
            descripcion=descripcion,
            fijo=fijo,
        )
        ingreso.save()

        return redirect('registrar_ingreso')
    
class EliminarIngreso(View):
    def post(self, request, ingreso_pk):

        # Esto tenemos que reemplazarlo por la persona autenticada en la aplicacion
        persona = get_object_or_404(Persona, pk=1)
        
        # Busca el ingreso por la pk que se pasa en la URL
        ingreso = get_object_or_404(Ingreso, pk=ingreso_pk)

        # Verifico si el ingreso pertenece a la persona
        if ingreso.persona == persona:
            ingreso.delete()
            messages.success(request, "Ingreso eliminado con éxito.")
        else:
            messages.error(request, "El ingreso no pertenece a la persona especificada.")

        return redirect('registrar_ingreso')
    