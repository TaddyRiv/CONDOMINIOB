from rest_framework import serializers
from app.models.apartamento import Apartamento
class ApartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartamento
        fields = ('id', 'numero', 'bloque', 'estado', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_numero(self, value):
        if not value.strip():
            raise serializers.ValidationError("El número de apartamento no puede estar vacío.")
        return value
    