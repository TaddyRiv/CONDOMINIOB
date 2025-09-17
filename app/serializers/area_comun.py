# AreaComun
from app.models import AreaComun
from rest_framework import serializers

class AreaComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaComun
        fields = ["id", "nombre", "estado", "capacidad", "reglas"]