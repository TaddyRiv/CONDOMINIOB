from rest_framework import mixins, viewsets, permissions
from app.serializers import UsuarioPropietarioCreateSerializer
from app.models.usuario import Usuario

class PropietarioUsuarioViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/usuarios-propietarios/ -> crea un Usuario con rol DUEÑO
    """
    serializer_class = UsuarioPropietarioCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Usuario.objects.none()
