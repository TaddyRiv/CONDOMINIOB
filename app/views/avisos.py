from rest_framework import viewsets, permissions
from app.models import Aviso, Usuario
from app.serializers.avisos import AvisoSerializer, AvisoResidenteSerializer


class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all().order_by("-fecha_publicacion")

    def get_permissions(self):
        """
        - ADMIN → puede crear, editar y eliminar.
        - RESIDENTE → solo puede leer.
        - Otros roles → sin acceso.
        """
        if self.request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """
        - Si es RESIDENTE → serializer reducido.
        - Si es ADMIN → serializer completo.
        """
        user = self.request.user
        if user.rol == Usuario.Roles.RESIDENTE:
            return AvisoResidenteSerializer
        return AvisoSerializer
