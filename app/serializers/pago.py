from rest_framework import serializers
from app.models.pago import Pago

class PagoSerializer(serializers.ModelSerializer):
    pagador_email = serializers.CharField(source="pagador.email", read_only=True)
    cargo_total = serializers.DecimalField(source="cargo.total", max_digits=10, decimal_places=2, read_only=True)
    cargo_pagado = serializers.DecimalField(source="cargo.pagado", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Pago
        fields = ["id", "cargo", "tipo", "pagador", "pagador_email", "monto",
                  "comprobante", "observacion", "estado", "verificado_por",
                  "fecha_verificacion", "created_at", "cargo_total", "cargo_pagado"]
        read_only_fields = ["estado", "verificado_por", "fecha_verificacion", "created_at"]

    def create(self, validated_data):
        # Si no te mandan pagador, usar el usuario autenticado
        request = self.context.get("request")
        if request and not validated_data.get("pagador"):
            validated_data["pagador"] = request.user
        return super().create(validated_data)
