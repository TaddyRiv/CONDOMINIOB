# app/views/visita.py
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from app.models.visita import Visita
from app.serializers.visita import VisitaSerializer, VisitaRegistrarSerializer


class VisitaViewSet(ModelViewSet):
    queryset = Visita.objects.select_related("visitante", "apartamento", "vehiculo")
    serializer_class = VisitaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()

        # Filtros
        apartamento = self.request.query_params.get("apartamento")
        visitante = self.request.query_params.get("visitante")
        ci = self.request.query_params.get("ci")
        nombre = self.request.query_params.get("nombre")
        placa = self.request.query_params.get("placa")
        activas = self.request.query_params.get("activas")
        fdesde = parse_date(self.request.query_params.get("fecha_desde") or "")
        fhasta = parse_date(self.request.query_params.get("fecha_hasta") or "")

        if apartamento:
            qs = qs.filter(apartamento_id=apartamento)
        if visitante:
            qs = qs.filter(visitante_id=visitante)
        if ci:
            qs = qs.filter(visitante__ci__iexact=ci)
        if nombre:
            qs = qs.filter(visitante__nombre__icontains=nombre)
        if placa:
            qs = qs.filter(vehiculo__placa__icontains=placa)
        if activas and activas.lower() == "true":
            qs = qs.filter(hora_salida__isnull=True)
        if fdesde:
            qs = qs.filter(fecha__gte=fdesde)
        if fhasta:
            qs = qs.filter(fecha__lte=fhasta)

        ordering = self.request.query_params.get("ordering")
        return qs.order_by(ordering) if ordering else qs.order_by("-created_at")

    # POST /api/visitas/registrar/
    def registrar(self, request, *args, **kwargs):
        ser = VisitaRegistrarSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        visita = ser.save()
        return Response(VisitaSerializer(visita).data, status=status.HTTP_201_CREATED)

    # Cuando se edita una visita (PUT/PATCH), si se setea hora_salida por 1ra vez, marcamos cerrado_por
    def perform_update(self, serializer):
        before = self.get_object()
        obj = serializer.save()
        if obj.hora_salida and not before.hora_salida:
            obj.cerrado_por = self.request.user
            obj.save(update_fields=["cerrado_por"])

    # POST /api/visitas/<id>/cerrar/  (cierra ahora o con hora enviada)
    @action(detail=True, methods=["post"], url_path="cerrar")
    def cerrar(self, request, pk=None):
        visita = self.get_object()
        if visita.hora_salida:
            return Response({"detail": "La visita ya está cerrada."}, status=400)

        hora_str = request.data.get("hora_salida")
        if hora_str:
            hora = parse_time(str(hora_str))
            if not hora:
                return Response(
                    {"hora_salida": ["Formato inválido. Use HH:MM o HH:MM:SS."]},
                    status=400,
                )
        else:
            hora = timezone.localtime().time()

        visita.hora_salida = hora
        visita.cerrado_por = request.user
        visita.save(update_fields=["hora_salida", "cerrado_por"])
        return Response(VisitaSerializer(visita).data)

    # GET /api/visitas/todos/  (sin paginación, respeta filtros)
    @action(detail=False, methods=["get"], url_path="todos")
    def listar_todos(self, request):
        qs = self.get_queryset()
        data = self.get_serializer(qs, many=True).data
        return Response(data)
