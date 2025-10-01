# app/views/pagos.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from app.models.pago import Pago
from app.serializers.pago import PagoSerializer
from app.permissions import IsAdminOrEmpleado  # <-- nuevo

class PagoViewSet(ModelViewSet):
    queryset = Pago.objects.select_related("cargo", "pagador", "verificado_por").order_by("-created_at")
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrEmpleado])
    def aprobar(self, request, pk=None):
        pago = self.get_object()
        if pago.estado != Pago.Estado.PENDIENTE:
            return Response({"detail": "El pago ya fue verificado."}, status=status.HTTP_400_BAD_REQUEST)
        pago.aprobar(request.user, request.data.get("observacion"))
        return Response(self.get_serializer(pago).data, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrEmpleado])
    def rechazar(self, request, pk=None):
        pago = self.get_object()
        if pago.estado != Pago.Estado.PENDIENTE:
            return Response({"detail": "El pago ya fue verificado."}, status=status.HTTP_400_BAD_REQUEST)
        pago.rechazar(request.user, request.data.get("observacion"))
        return Response(self.get_serializer(pago).data, status=200)
