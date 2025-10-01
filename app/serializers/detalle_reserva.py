from django.db import transaction
from rest_framework import serializers
from app.models.reserva import Reserva
from app.models.detalle_reserva import DetalleReserva


class DetalleReservaCreateSerializer(serializers.ModelSerializer):               # para crear detalles de reserva
    class Meta:
        model = DetalleReserva
        fields = ["id", "reserva", "descripcion"]
    @transaction.atomic                                                          #-- atomic para que no falle si hay error
    def create(self, validated_data):
        request = self.context["request"]
        reserva: Reserva = validated_data["reserva"]
        user = request.user
        rol = getattr(user, "rol", "")
        if not (rol.upper() in ["ADMIN", "EMPLEADO"] or reserva.usuario_id == user.id):
            raise serializers.ValidationError("No puedes agregar detalles a reservas de otro usuario.") #-- permisos
        return super().create(validated_data) 