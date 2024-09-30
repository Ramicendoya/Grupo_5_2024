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
    
class Ahorro(models.Model):
    personas = models.ForeignKey(Persona, on_delete=models.CASCADE)
    meta = models.ForeignKey(Meta, on_delete=models.CASCADE)
    fecha_ahorro = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def str(self):
        return f"Ahorro de {self.monto} para {self.meta}"

class Ingreso(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()

    def str(self):
        return f"Ingreso de {self.monto} el {self.fecha}"

class Gasto(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def str(self):
        return f"Gasto de {self.monto} en {self.categoria} el {self.fecha}"