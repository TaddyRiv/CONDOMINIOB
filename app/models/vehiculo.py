from django.db import models
from django.core.exceptions import ValidationError
from app.models.apartamento import Apartamento

class Vehiculo(models.Model):
    placa = models.CharField(max_length=15, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    # Si pertenece a un apartamento ⇒ es vehículo de RESIDENTE
    apartamento = models.ForeignKey(
        Apartamento, on_delete=models.PROTECT,
        related_name="vehiculos", blank=True, null=True
    )

    # Solo los vehículos enlazados a apartamento pueden tener pase/placa conocida
    pase_conocido = models.BooleanField(default=False)

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehiculos"
        indexes = [
            models.Index(fields=["placa"]),
            models.Index(fields=["apartamento", "placa"]),
        ]
        ordering = ["placa"]

    def clean(self):
        # Si se marca pase_conocido, debe pertenecer a un apartamento
        if self.pase_conocido and self.apartamento is None:
            raise ValidationError("Solo los vehículos asignados a un apartamento pueden tener pase conocido.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def es_residente(self) -> bool:
        return self.apartamento_id is not None

    def __str__(self):
        dueño = f" (Apto {self.apartamento.numero})" if self.apartamento_id else " (visitante)"
        return f"{self.placa}{dueño}"
