# DetalleReserva
from django.db import transaction
from rest_framework import serializers
from app.models.reserva import Reserva
from app.models.detalle_reserva import DetalleReserva


class DetalleReservaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleReserva
        fields = ["id", "reserva", "descripcion"]
    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        reserva: Reserva = validated_data["reserva"]
        user = request.user
        rol = getattr(user, "rol", "")
        if not (rol.upper() in ["ADMIN", "EMPLEADO"] or reserva.usuario_id == user.id):
            raise serializers.ValidationError("No puedes agregar detalles a reservas de otro usuario.")
        return super().create(validated_data)
