from django.db import models
from django.utils import timezone


class Aviso(models.Model):
    propietario = models.ForeignKey(
        "Usuario",                        # Se relaciona con el usuario que crea el aviso
        on_delete=models.CASCADE,
        related_name="avisos_propietario"
    )
    titulo = models.CharField(max_length=255)   # Título del aviso
    descripcion = models.TextField()            # Contenido del aviso
    fecha_publicacion = models.DateTimeField(default=timezone.now)  # Fecha de creación

    def __str__(self):
        return f"{self.titulo} - {self.propietario.nombre}"
#cambios noel