from rest_framework import serializers
from app.models.visitante import Visitante

class VisitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitante
        fields = ["id", "nombre", "ci", "celular", "activo"]
        read_only_fields = ["activo"]
