from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from app.models.usuario import Usuario
from app.permissions import IsAdminOrEmpleado, IsAuthenticatedAndActive
from app.serializers.usuario import (
    UsuarioListSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    
)
from rest_framework.parsers import JSONParser

from rest_framework import status
from rest_framework.response import Response

class UsuarioViewSet(ModelViewSet):
    queryset = Usuario.objects.all().order_by("id")
    serializer_class = UsuarioListSerializer
    parser_classes = [JSONParser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["username", "email", "nombre", "ci", "rol"]
    ordering_fields = ["id", "username", "email", "nombre", "ci", "rol", "date_joined"]
    ordering = ["id"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminOrEmpleado()]
        return [IsAuthenticatedAndActive()]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        if self.action in ("update", "partial_update"):
            return UsuarioUpdateSerializer
        return UsuarioListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    # 👇 este método es opcional, solo si habías modificado create
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # ✅ devolver SOLO el creado
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    

class ResidenteUsuarioViewSet(ModelViewSet):
    queryset = Usuario.objects.filter(rol=Usuario.Roles.RESIDENTE).order_by("id")

    def get_permissions(self):
        if self.action == "create":
            return [IsAdminOrEmpleado()]
        return [IsAuthenticatedAndActive()]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        if self.action in ("update", "partial_update"):
            return UsuarioUpdateSerializer
        return UsuarioListSerializer