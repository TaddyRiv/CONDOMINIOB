from rest_framework import viewsets, permissions, mixins
from app.models.apartamento import Apartamento
from app.serializers import ApartamentoSerializer
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication

class ApartamentoViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,   # opcional: listar
                         viewsets.GenericViewSet):
    queryset = Apartamento.objects.all()
    serializer_class = ApartamentoSerializer
    permission_classes = [permissions.IsAuthenticated]  # o IsAdminUser si solo admin crea


class ApartamentoListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Apartamento.objects.all().order_by("bloque", "numero")
    serializer_class = ApartamentoSerializer