from django.db import models

#DETALLE_RESERVA

class DetalleReserva(models.Model):
    reserva = models.ForeignKey(
        "app.Reserva", on_delete=models.CASCADE, related_name="detalles"
    )
    descripcion = models.TextField()
    # opcional: puedes agregar ítems, recursos, cantidades, costos, etc.
    # recurso = models.CharField(max_length=60, blank=True)
    # cantidad = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f"Detalle #{self.id} de Reserva {self.reserva_id}"