from rest_framework import serializers
from app.models.usuario import Usuario

class UsuarioRegistroRostroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "email", "nombre", "foto"]


class VerificarAccesoSerializer(serializers.Serializer):
    foto = serializers.CharField()
    camara_id = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=[("ENTRADA", "Entrada"), ("SALIDA", "Salida")])
