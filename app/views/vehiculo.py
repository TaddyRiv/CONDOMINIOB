from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from app.models.vehiculo import Vehiculo
from app.serializers.vehiculo import VehiculoSerializer
from rest_framework import serializers

class VehiculoViewSet(ModelViewSet):
    queryset = Vehiculo.objects.select_related("apartamento")
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        apartamento = self.request.query_params.get("apartamento")
        placa = self.request.query_params.get("placa")
        solo_residentes = self.request.query_params.get("residentes")  # 'true' para filtrar
        if apartamento:
            qs = qs.filter(apartamento_id=apartamento)
        if placa:
            qs = qs.filter(placa__iexact=placa)
        if solo_residentes and solo_residentes.lower() == "true":
            qs = qs.exclude(apartamento__isnull=True)
        return qs

    @action(detail=False, methods=["get"])
    def por_placa(self, request):
        """Búsqueda directa por placa exacta (case-insensitive)."""
        placa = request.query_params.get("placa")
        if not placa:
            return Response({"detail": "Falta parámetro 'placa'."}, status=400)
        veh = Vehiculo.objects.select_related("apartamento").filter(placa__iexact=placa).first()
        if not veh:
            return Response({"detail": "No encontrado."}, status=404)
        return Response(self.get_serializer(veh).data)
