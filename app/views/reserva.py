from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from app.models import Reserva
from app.serializers import ReservaSerializer, ReservaEstadoSerializer
from app.permissions import IsAuthenticatedAndActive, IsOwnerOrAdmin, IsAdminOrEmpleado

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related("area_comun", "usuario").all()
    serializer_class = ReservaSerializer
    def get_queryset(self):
        user = self.request.user
        rol = getattr(user, "rol", "").upper()
        if rol in ["ADMIN", "EMPLEADO"]:
            return self.queryset
        return self.queryset.filter(usuario=user)
    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticatedAndActive(), IsOwnerOrAdmin()]
        return [IsAuthenticatedAndActive()]
    def perform_create(self, serializer):
        serializer.save()
    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAuthenticatedAndActive, IsAdminOrEmpleado])
    def aprobar(self, request, pk=None):
        reserva = self.get_object()
        ser = ReservaEstadoSerializer(reserva, data={"estado": "APROBADA"}, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"ok": True, "estado": "APROBADA"}, status=status.HTTP_200_OK)
    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAuthenticatedAndActive, IsAdminOrEmpleado])
    def completar(self, request, pk=None):
        reserva = self.get_object()
        ser = ReservaEstadoSerializer(reserva, data={"estado": "COMPLETADA"}, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"ok": True, "estado": "COMPLETADA"}, status=status.HTTP_200_OK)
    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAuthenticatedAndActive, IsOwnerOrAdmin])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        ser = ReservaEstadoSerializer(reserva, data={"estado": "CANCELADA"}, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"ok": True, "estado": "CANCELADA"}, status=status.HTTP_200_OK)