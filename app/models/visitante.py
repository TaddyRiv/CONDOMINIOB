# app/models/visitante.py
from django.db import models

class Visitante(models.Model):
    nombre = models.CharField(max_length=150)
    ci = models.CharField(max_length=30, blank=True, null=True)
    celular = models.CharField(max_length=30, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "visitantes"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.ci or 's/CI'})"
