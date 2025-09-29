from rest_framework import serializers
from app.models import Aviso


class AvisoSerializer(serializers.ModelSerializer):
    """Serializer completo (para ADMIN)"""
    propietario_nombre = serializers.CharField(source="propietario.nombre", read_only=True)

    class Meta:
        model = Aviso
        fields = ["id", "titulo", "descripcion", "fecha_publicacion", "propietario", "propietario_nombre"]
        read_only_fields = ["propietario"]

    def create(self, validated_data):
        """
        Al crear un aviso, se asigna automáticamente
        el usuario autenticado como propietario.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["propietario"] = request.user
        return super().create(validated_data)


class AvisoResidenteSerializer(serializers.ModelSerializer):
    """Serializer reducido (para RESIDENTE: solo lectura)"""
    class Meta:
        model = Aviso
        fields = ["titulo", "descripcion", "fecha_publicacion"]