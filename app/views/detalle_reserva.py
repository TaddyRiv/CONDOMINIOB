from rest_framework import viewsets
from app.models import DetalleReserva
from app.serializers import DetalleReservaCreateSerializer
from app.permissions import IsAuthenticatedAndActive, IsOwnerOrAdmin

class DetalleReservaViewSet(viewsets.ModelViewSet):
    queryset = DetalleReserva.objects.select_related("reserva", "reserva__usuario").all()
    serializer_class = DetalleReservaCreateSerializer
    def get_queryset(self):
        user = self.request.user
        rol = getattr(user, "rol", "").upper()
        if rol in ["ADMIN", "EMPLEADO"]:
            return self.queryset
        return self.queryset.filter(reserva__usuario=user)
    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticatedAndActive(), IsOwnerOrAdmin()]
        return [IsAuthenticatedAndActive()]