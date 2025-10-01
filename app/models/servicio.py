from django.db import models

class Servicio(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "servicios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
