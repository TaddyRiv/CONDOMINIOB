# app/views/entrada_salida.py
from rest_framework import viewsets
from app.models.acceso import EntradaSalida
from app.serializers.entrada_salida import EntradaSalidaSerializer

class EntradaSalidaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EntradaSalida.objects.select_related(
        "intento__usuario"
    ).order_by("-fecha", "-hora")
    serializer_class = EntradaSalidaSerializer
