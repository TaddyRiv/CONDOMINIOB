from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from app.models.cargo import Cargo
from app.serializers.cargo import CargoSerializer

class CargoViewSet(ModelViewSet):
    queryset = Cargo.objects.select_related("apartamento").prefetch_related("detalles__servicio")
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def recomputar(self, request, pk=None):
        cargo = self.get_object()
        cargo.recomputar_total()
        serializer = self.get_serializer(cargo)
        return Response(serializer.data)
