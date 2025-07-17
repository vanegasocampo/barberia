from django.db import models
from django.contrib.auth.models import User

class Barberia(models.Model):
    dueño = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Barbero(models.Model):
    barberia = models.ForeignKey(Barberia, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    barberia = models.ForeignKey(Barberia, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    duracion = models.DurationField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} ({self.precio} COP)"

class Cita(models.Model):
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cliente_nombre = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20)
    fecha_hora = models.DateTimeField()
    confirmada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente_nombre} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
