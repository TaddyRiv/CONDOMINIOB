from rest_framework import mixins, viewsets, permissions
from app.serializers import UsuarioPropietarioCreateSerializer
from app.models.usuario import Usuario
from rest_framework import generics, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from app.permissions import IsAdminRole

class PropietarioUsuarioViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/usuarios-propietarios/ -> crea un Usuario con rol DUEÑO
    """
    serializer_class = UsuarioPropietarioCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Usuario.objects.none()

class UsuarioPropietarioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("id", "nombre", "ci", "email", "telefono", "rol", "fecha_nacimiento", "is_active")
        read_only_fields = ("rol",)

class PropietarioListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UsuarioPropietarioListSerializer

    def get_queryset(self):
        # Ajusta el nombre del rol si en tu modelo es "DUEÑO" o "PROPIETARIO"
        return Usuario.objects.filter(rol=Usuario.Roles.DUEÑO).order_by("nombre", "email")

class PropietarioDetailUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = UsuarioPropietarioListSerializer

    def get_queryset(self):
        return Usuario.objects.filter(rol=Usuario.Roles.DUEÑO)

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated()]