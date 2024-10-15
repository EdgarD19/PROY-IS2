from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class EspacioTrabajo(models.Model):
    nombre = models.CharField(max_length=100)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='espacios_propios')
    usuarios = models.ManyToManyField(User, related_name='espacios_asignados')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Tablero(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    espacio_trabajo = models.ForeignKey(EspacioTrabajo, on_delete=models.CASCADE, related_name='tableros')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Lista(models.Model):
    nombre = models.CharField(max_length=100)
    tablero = models.ForeignKey(Tablero, on_delete=models.CASCADE, related_name='listas')
    orden = models.IntegerField(default=0)
    max_wip = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['orden']
