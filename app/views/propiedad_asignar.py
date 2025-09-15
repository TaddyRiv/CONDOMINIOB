from rest_framework import mixins, viewsets, permissions
from app.serializers import PropiedadAsignarSerializer
from app.models.propiedad import Propiedad

class PropiedadAsignacionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/propiedades/ -> asigna Propiedad (dueño ↔ apartamento).
    Si "vive"=true, también crea Residencia.
    """
    serializer_class = PropiedadAsignarSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Propiedad.objects.none()
