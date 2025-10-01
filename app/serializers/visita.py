from rest_framework import serializers
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError

from app.models.visita import Visita
from app.models.visitante import Visitante
from app.models.vehiculo import Vehiculo
from app.models.apartamento import Apartamento  # <-- importa el modelo

class VisitaSerializer(serializers.ModelSerializer):
    visitante_nombre = serializers.CharField(source="visitante.nombre", read_only=True)
    apartamento_numero = serializers.CharField(source="apartamento.numero", read_only=True)
    vehiculo_placa = serializers.CharField(source="vehiculo.placa", read_only=True)

    class Meta:
        model = Visita
        fields = [
            "id", "visitante", "visitante_nombre", "apartamento", "apartamento_numero",
            "vehiculo", "vehiculo_placa", "detalle", "fecha", "hora_inicio", "hora_salida",
            "registrado_por", "cerrado_por", "created_at"
        ]
        read_only_fields = ["registrado_por", "cerrado_por", "created_at"]


class VisitaRegistrarSerializer(serializers.Serializer):
    """
    POST /visitas/registrar/
    {
      "apartamento": 5,
      "detalle": "Reunión",
      "visitante": { "nombre": "...", "ci": "...", "celular": "..." },
      "vehiculo": { "placa": "ABC123", "descripcion": "...", "apartamento": 5, "pase_conocido": true }  // opcional
    }
    """
    apartamento = serializers.IntegerField()
    detalle = serializers.CharField(required=False, allow_blank=True)
    visitante = serializers.DictField()
    vehiculo = serializers.DictField(required=False)

    def validate(self, attrs):
        # Normaliza strings
        if "detalle" in attrs and attrs["detalle"] is not None:
            attrs["detalle"] = attrs["detalle"].strip()

        # Visitante: nombre requerido
        v = attrs.get("visitante") or {}
        nombre = (v.get("nombre") or "").strip()
        if not nombre:
            raise serializers.ValidationError({"visitante": "El nombre del visitante es requerido."})
        v["nombre"] = nombre
        v["ci"] = (v.get("ci") or "").strip() or None
        v["celular"] = (v.get("celular") or "").strip() or None
        attrs["visitante"] = v

        # Vehículo opcional: si viene, placa requerida; normaliza
        veh = attrs.get("vehiculo")
        if veh:
            placa = (veh.get("placa") or "").strip().upper()
            if not placa:
                raise serializers.ValidationError({"vehiculo": "Placa requerida si envías 'vehiculo'."})
            veh["placa"] = placa
            veh["descripcion"] = (veh.get("descripcion") or "").strip() or None
            # Si marca pase_conocido, requiere apartamento
            pase = bool(veh.get("pase_conocido", False))
            veh["pase_conocido"] = pase
            if pase and not veh.get("apartamento"):
                raise serializers.ValidationError({"vehiculo": "Si 'pase_conocido' es true, debes indicar 'apartamento' del vehículo."})
            attrs["vehiculo"] = veh

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")

        # 1) Apartamento válido
        apto_id = validated_data["apartamento"]
        apto = Apartamento.objects.filter(pk=apto_id).first()
        if not apto:
            raise serializers.ValidationError({"apartamento": "Apartamento inválido."})

        # 2) Visitante: busca por CI (si trae), si no, crea
        vdata = validated_data["visitante"]
        visitante = None
        if vdata.get("ci"):
            visitante = Visitante.objects.filter(ci=vdata["ci"]).first()
        if not visitante:
            visitante = Visitante.objects.create(
                nombre=vdata["nombre"],
                ci=vdata["ci"],
                celular=vdata["celular"],
            )

        # 3) Vehículo (opcional) con validación de modelo
        vehiculo_obj = None
        veh = validated_data.get("vehiculo")
        if veh:
            placa = veh["placa"]
            vehiculo_obj = Vehiculo.objects.filter(placa__iexact=placa).first()
            if not vehiculo_obj:
                vehiculo_obj = Vehiculo(
                    placa=placa,
                    descripcion=veh.get("descripcion"),
                    apartamento_id=veh.get("apartamento"),  # None si es visitante
                    pase_conocido=veh.get("pase_conocido", False),
                )
                try:
                    # Dispara model.clean()/validators si los tienes
                    vehiculo_obj.full_clean()
                    vehiculo_obj.save()
                except DjangoValidationError as e:
                    # Devuelve 400 con mensajes claros en vez de 500
                    raise serializers.ValidationError({"vehiculo": e.message_dict or e.messages})

        # 4) Crear visita
        try:
            visita = Visita.objects.create(
                visitante=visitante,
                apartamento=apto,
                vehiculo=vehiculo_obj,
                detalle=validated_data.get("detalle", "") or "",
                registrado_por=getattr(request, "user", None),
            )
        except IntegrityError:
            raise serializers.ValidationError({"detail": "Error de integridad al crear la visita."})

        return visita

    def to_representation(self, visita: Visita):
        return VisitaSerializer(visita).data
