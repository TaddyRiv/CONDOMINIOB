from django.db import models
from django.conf import settings
from django.db.models import Q
from app.models.apartamento import Apartamento

Usuario = settings.AUTH_USER_MODEL

class Propiedad(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='propiedades')
    apartamento = models.ForeignKey(Apartamento, on_delete=models.PROTECT, related_name='propiedades')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)  # null = propiedad vigente
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'propiedades'
        ordering = ['-created_at']
        # Regla: solo UN propietario ACTIVO por apartamento
        constraints = [
            models.UniqueConstraint(
                fields=['apartamento'],
                condition=Q(fecha_fin__isnull=True),
                name='uniq_propiedad_activa_por_apartamento'
            )
        ]

    def __str__(self):
        return f"{self.usuario} dueño de {self.apartamento} ({self.fecha_inicio} - {self.fecha_fin or 'vigente'})"
