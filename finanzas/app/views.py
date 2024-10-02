from django.shortcuts import render, redirect
from django.http import HttpResponse
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