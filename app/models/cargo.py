# app/models/cargo.py
from django.db import models
from django.conf import settings
from app.models.apartamento import Apartamento
from django.db.models import Sum

Usuario = settings.AUTH_USER_MODEL

class Cargo(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PARCIAL   = "PARCIAL", "Parcialmente pagado"
        PAGADO    = "PAGADO", "Pagado"

    apartamento = models.ForeignKey(Apartamento, on_delete=models.PROTECT, related_name="cargos")
    periodo = models.DateField(help_text="Usa el primer día del mes, p. ej. 2025-09-01")
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    total  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    creado_por = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name="cargos_creados")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cargos"
        ordering = ["-periodo", "-created_at"]
        unique_together = [("apartamento", "periodo")]  # opcional

    def __str__(self):
        return f"Cargo {self.apartamento} {self.periodo:%Y-%m}"

    # Se apoya en related_name="detalles" desde CargoServicio
    def recomputar_total(self):
        agg = self.detalles.aggregate(s=Sum("subtotal"))
        self.total = agg["s"] or 0
        self.saldo = (self.total or 0) - (self.pagado or 0)
        self._actualizar_estado_por_saldo()
        self.save(update_fields=["total", "saldo", "estado"])

    # Se apoya en related_name="pagos" desde Pago
    def aplicar_pago_aprobado(self):
        from django.db.models import Sum  # local para evitar ciclos
        agg = self.pagos.filter(estado="APROBADO").aggregate(m=Sum("monto"))
        self.pagado = agg["m"] or 0
        self.saldo = (self.total or 0) - (self.pagado or 0)
        self._actualizar_estado_por_saldo()
        self.save(update_fields=["pagado", "saldo", "estado"])

    def _actualizar_estado_por_saldo(self):
        if self.saldo <= 0:
            self.estado = Cargo.Estado.PAGADO
            self.saldo = 0
        elif self.pagado > 0:
            self.estado = Cargo.Estado.PARCIAL
        else:
            self.estado = Cargo.Estado.PENDIENTE
