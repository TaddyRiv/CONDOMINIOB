# app/serializers/entrada_salida.py
from rest_framework import serializers
from app.models.acceso import EntradaSalida

class EntradaSalidaSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()

    class Meta:
        model = EntradaSalida
        fields = ["id", "fecha", "hora", "tipo", "usuario"]

    def get_usuario(self, obj):
        if obj.intento and obj.intento.usuario:
            return {
                "id": obj.intento.usuario.id,
                "nombre": obj.intento.usuario.nombre,
                "email": obj.intento.usuario.email,
                "rol": obj.intento.usuario.rol
            }
        return None
