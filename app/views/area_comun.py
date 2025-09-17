
from rest_framework import viewsets
from app.models import AreaComun
from app.serializers import AreaComunSerializer
from app.permissions import IsAuthenticatedAndActive, IsAdminOrEmpleado

class AreaComunViewSet(viewsets.ModelViewSet):
    queryset = AreaComun.objects.all().order_by("nombre")
    serializer_class = AreaComunSerializer
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticatedAndActive()]
        return [IsAuthenticatedAndActive(), IsAdminOrEmpleado()]