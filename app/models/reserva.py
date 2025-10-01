from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Reserva(models.Model):
    ESTADOS = (
        ("PENDIENTE", "PENDIENTE"),
        ("APROBADA", "APROBADA"),
        ("CANCELADA", "CANCELADA"),
        ("COMPLETADA", "COMPLETADA"),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reservas"
    )
    area_comun = models.ForeignKey(
        "app.AreaComun", on_delete=models.PROTECT, related_name="reservas"
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=12, choices=ESTADOS, default="PENDIENTE")
    fecha_creacion = models.DateTimeField(default=timezone.now)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha", "-hora_inicio"]
        indexes = [
            models.Index(fields=["area_comun", "fecha"]),
            models.Index(fields=["estado"]),
        ]

    def clean(self): # validar solapamientos y estado area
        # Solo validar si ambos campos existen
        if not self.hora_inicio or not self.hora_fin:
            return

        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser menor a la hora de fin.")

        if self.area_comun and getattr(self.area_comun, "estado", "ACTIVO") != "ACTIVO":
            raise ValidationError("El área común no está disponible (inactiva).")

        qs = Reserva.objects.filter(
            area_comun=self.area_comun, fecha=self.fecha
        ).exclude(pk=self.pk)
        if qs.filter(
            hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio
        ).exists():
            raise ValidationError(
                "Ya existe una reserva solapada en esa franja horaria para el área."
            )