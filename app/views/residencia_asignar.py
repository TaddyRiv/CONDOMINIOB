from rest_framework import mixins, viewsets, permissions
from app.serializers import ResidenciaAsignarSerializer
from app.models.residencia import Residencia

class ResidenciaAsignacionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/residencias/ -> crea la Residencia (usuario ↔ apartamento)
    """
    serializer_class = ResidenciaAsignarSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Residencia.objects.none()
