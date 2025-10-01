from django.db import models
from django.utils import timezone

from app.models.visitante import Visitante
from app.models.apartamento import Apartamento
from app.models.vehiculo import Vehiculo
from app.models.usuario import Usuario


# ✅ Callable importable para el default de hora_inicio
def current_local_time():
    return timezone.localtime().time()


class Visita(models.Model):
    # Tabla intermedia Visitante ⇄ Apartamento
    visitante = models.ForeignKey(Visitante, on_delete=models.PROTECT, related_name="visitas")
    apartamento = models.ForeignKey(Apartamento, on_delete=models.PROTECT, related_name="visitas")

    # Vehículo usado en esta visita (opcional)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, blank=True, null=True, related_name="visitas")

    detalle = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateField(default=timezone.localdate)          # OK
    hora_inicio = models.TimeField(default=current_local_time)    # ✅ sin lambda
    hora_salida = models.TimeField(blank=True, null=True)

    # Guardia/usuario que registra y cierra
    registrado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitas_registradas"
    )
    cerrado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitas_cerradas"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "visitas"
        indexes = [
            models.Index(fields=["fecha", "apartamento"]),
            models.Index(fields=["visitante", "apartamento"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        base = f"{self.visitante} → Apto {self.apartamento.numero} ({self.fecha})"
        if self.vehiculo_id:
            base += f" - Vehículo {self.vehiculo.placa}"
        return base
