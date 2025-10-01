from rest_framework import serializers
from app.models.acceso import (
    PuntoAcceso,
    Camara,
    Reconocimiento,
    IntentoAcceso,
    EntradaSalida
)
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo


class PuntoAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoAcceso
        fields = "__all__"


class CamaraSerializer(serializers.ModelSerializer):
    punto_acceso = PuntoAccesoSerializer(read_only=True)
    punto_acceso_id = serializers.PrimaryKeyRelatedField(
        queryset=PuntoAcceso.objects.all(), source="punto_acceso", write_only=True
    )

    class Meta:
        model = Camara
        fields = ["id", "nombre", "ubicacion", "activa", "punto_acceso", "punto_acceso_id"]


class ReconocimientoSerializer(serializers.ModelSerializer):
    camara = CamaraSerializer(read_only=True)
    camara_id = serializers.PrimaryKeyRelatedField(
        queryset=Camara.objects.all(), source="camara", write_only=True
    )

    class Meta:
        model = Reconocimiento
        fields = ["id", "tipo", "captura", "timestamp", "camara", "camara_id"]


class IntentoAccesoSerializer(serializers.ModelSerializer):
    reconocimiento = ReconocimientoSerializer(read_only=True)
    reconocimiento_id = serializers.PrimaryKeyRelatedField(
        queryset=Reconocimiento.objects.all(), source="reconocimiento", write_only=True
    )

    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), allow_null=True, required=False
    )
    vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = IntentoAcceso
        fields = [
            "id", "reconocimiento", "reconocimiento_id",
            "usuario", "vehiculo", "resultado", "motivo", "accion"
        ]


class EntradaSalidaSerializer(serializers.ModelSerializer):
    intento = IntentoAccesoSerializer(read_only=True)
    intento_id = serializers.PrimaryKeyRelatedField(
        queryset=IntentoAcceso.objects.all(), source="intento", write_only=True
    )

    class Meta:
        model = EntradaSalida
        fields = ["id", "intento", "intento_id", "fecha", "hora", "tipo"]
