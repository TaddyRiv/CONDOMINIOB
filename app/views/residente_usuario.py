from rest_framework import mixins, viewsets, permissions
from app.serializers import UsuarioResidenteCreateSerializer
from app.models.usuario import Usuario

class ResidenteUsuarioViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/usuarios-residentes/ -> crea un Usuario con rol RESIDENTE
    """
    serializer_class = UsuarioResidenteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Usuario.objects.none()
