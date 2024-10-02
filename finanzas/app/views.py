from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'home.html') 

def Prueba(request):
    return render(request, 'prueba2.html') 