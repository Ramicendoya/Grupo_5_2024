from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'home.html') 

def ingresos(request):
    return render(request, 'ingresos.html') 

def gastos(request):
    return render(request, 'gastos.html') 