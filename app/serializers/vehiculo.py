from rest_framework import serializers
from app.models.vehiculo import Vehiculo

class VehiculoSerializer(serializers.ModelSerializer):
    apartamento_numero = serializers.CharField(source="apartamento.numero", read_only=True)

    class Meta:
        model = Vehiculo
        fields = ["id", "placa", "descripcion", "apartamento", "apartamento_numero",
                  "pase_conocido", "activo", "created_at"]
        read_only_fields = ["activo", "created_at"]

    def validate(self, attrs):
        # Si marca pase_conocido, debe estar asignado a un apartamento (regla de negocio)
        if attrs.get("pase_conocido") and not (attrs.get("apartamento") or getattr(self.instance, "apartamento", None)):
            raise serializers.ValidationError("pase_conocido requiere un apartamento asignado.")
        return attrs
 