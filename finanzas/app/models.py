from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cuil = models.BigIntegerField()
    fecha_nacimiento = models.DateField()
    bl_baja = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    detalle = models.TextField(null=True, blank=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, null=True)
    bl_baja = models.BooleanField(default=False)
    bl_general = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Ingreso(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=4)
    descripcion = models.TextField(null=True, blank=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    bl_fijo = models.BooleanField(default=False)
    bl_baja = models.BooleanField(default=False)
    metodo_pago = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.nombre


class Gasto(models.Model):
    monto = models.DecimalField(max_digits=12, decimal_places=4)
    observaciones = models.TextField(null=True, blank=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    bl_fijo = models.BooleanField(default=False)
    bl_baja = models.BooleanField(default=False)
    metodo_pago = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"Gasto de {self.monto} - {self.persona}"


class MovimientoIngreso(models.Model):
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=4)
    fecha = models.DateField()
    bl_baja = models.BooleanField(default=False)

    def __str__(self):
        return f"Movimiento de ingreso: {self.ingreso}"


class MovimientoGasto(models.Model):
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=4)
    fecha = models.DateField()
    bl_baja = models.BooleanField(default=False)

    def __str__(self):
        return f"Movimiento de gasto: {self.gasto}"


class Recurrencia(models.Model):
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField(null=True, blank=True)
    frecuencia = models.IntegerField()
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE, null=True, blank=True)
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE, null=True, blank=True)
    bl_baja = models.BooleanField(default=False)

    def __str__(self):
        return f"Recurrencia desde {self.fecha_desde} hasta {self.fecha_hasta}"