from rest_framework import mixins, viewsets, permissions
from app.serializers import UsuarioResidenteCreateSerializer
from app.models.usuario import Usuario
from rest_framework import generics, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication


class ResidenteUsuarioViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/usuarios-residentes/ -> crea un Usuario con rol RESIDENTE
    """
    serializer_class = UsuarioResidenteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Usuario.objects.none()
class UsuarioResidenteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("id", "nombre", "ci", "email", "telefono", "rol", "fecha_nacimiento", "is_active")
        read_only_fields = ("rol",)

class ResidenteListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UsuarioResidenteListSerializer

    def get_queryset(self):
        return Usuario.objects.filter(rol=Usuario.Roles.RESIDENTE).order_by("nombre", "email")
