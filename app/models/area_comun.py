from django.db import models


class AreaComun(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    estado = models.CharField(max_length=20, default="ACTIVO")  # ACTIVO/INACTIVO
    # opcional: capacidad, reglas, horarios permitidos, costo por hora, etc.
    capacidad = models.PositiveIntegerField(null=True, blank=True)
    reglas = models.TextField(blank=True)
    def __str__(self):
        return self.nombre