from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    recurrencia = models.CharField(max_length=50)
    fecha_fin = models.DateField(null=True, blank=True)
    fecha_inicio = models.DateField()

    def __str__(self):
        return self.nombre

class Meta(models.Model):
    nombre = models.CharField(max_length=100)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre