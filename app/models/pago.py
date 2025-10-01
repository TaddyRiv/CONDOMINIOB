# app/models/pago.py
from django.db import models
from django.utils import timezone
from django.conf import settings

Usuario = settings.AUTH_USER_MODEL

def upload_comprobante(instance, filename):
    return f"pagos/comprobantes/cargo_{instance.cargo_id}/{filename}"

class Pago(models.Model):
    class Tipo(models.TextChoices):
        QR = "QR", "QR"
        EFECTIVO = "EFECTIVO", "Efectivo"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO  = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    cargo = models.ForeignKey('app.Cargo', on_delete=models.CASCADE, related_name="pagos")
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    pagador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="pagos_realizados")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante = models.FileField(upload_to=upload_comprobante, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    verificado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="pagos_verificados"
    )
    fecha_verificacion = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pagos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pago {self.id} - Cargo {self.cargo_id} - {self.monto} ({self.tipo})"

    def aprobar(self, admin_user, observacion: str | None = None):
        self.estado = Pago.Estado.APROBADO
        self.verificado_por = admin_user
        self.fecha_verificacion = timezone.now()
        if observacion:
            self.observacion = observacion
        self.save()
        self.cargo.aplicar_pago_aprobado()

    def rechazar(self, admin_user, observacion: str | None = None):
        self.estado = Pago.Estado.RECHAZADO
        self.verificado_por = admin_user
        self.fecha_verificacion = timezone.now()
        if observacion:
            self.observacion = observacion
        self.save()
        self.cargo.aplicar_pago_aprobado()
