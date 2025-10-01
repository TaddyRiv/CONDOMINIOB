from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import serializers

from app.models.reserva import Reserva


#-- permitimos formato de horario solo horas y minutos

class TimeHMField(serializers.TimeField):
    """
    Acepta y muestra horas en formato HH:MM.
    Fuerza segundos y microsegundos a cero.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%H:%M")           # salida: HH:MM
        kwargs.setdefault("input_formats", ["%H:%M"])  # entrada: HH:MM
        super().__init__(*args, **kwargs)

    def to_internal_value(self, value):
        t = super().to_internal_value(value)
        return t.replace(second=0, microsecond=0)


class EstadoChoiceField(serializers.ChoiceField):
    """
    ChoiceField tolerante para estado.
    - Acepta mayúsculas y minúsculas.
    - Normaliza variantes en masculino -> femenino.
    """
    def to_internal_value(self, data):
        if isinstance(data, str):
            val = data.strip().upper()

            mapping = {
                "APROBADO": "APROBADA",
                "CANCELADO": "CANCELADA",
                "COMPLETADO": "COMPLETADA",
            }
            if val in mapping:
                val = mapping[val]

            if val in ["PENDIENTE", "APROBADA", "CANCELADA", "COMPLETADA"]:
                data = val

        return super().to_internal_value(data)


# ---------- Serializers ----------

class ReservaSerializer(serializers.ModelSerializer):
    usuario_id = serializers.IntegerField(read_only=True)
    area_comun_nombre = serializers.CharField(source="area_comun.nombre", read_only=True)

    # horas solo HH:MM
    hora_inicio = TimeHMField()
    hora_fin = TimeHMField()

    # permitir setear estado desde la API con normalización y case-insensitive
    estado = EstadoChoiceField(choices=[c[0] for c in Reserva.ESTADOS], required=False)

    class Meta:
        model = Reserva
        fields = [
            "id",
            "usuario_id",
            "area_comun",
            "area_comun_nombre",
            "fecha",
            "hora_inicio",
            "hora_fin",
            "estado",
            "fecha_creacion",
            "descripcion",
        ]
        read_only_fields = ["fecha_creacion"]

    def validate(self, attrs):
        hi = attrs.get("hora_inicio") or getattr(self.instance, "hora_inicio", None)
        hf = attrs.get("hora_fin") or getattr(self.instance, "hora_fin", None)
        if hi and hf and hi >= hf:
            raise serializers.ValidationError("La hora de inicio debe ser menor a la hora de fin.")

        area = attrs.get("area_comun") or getattr(self.instance, "area_comun", None)
        if area and area.estado != "ACTIVO":
            raise serializers.ValidationError("El área común no está disponible (inactiva).")

        fecha = attrs.get("fecha") or getattr(self.instance, "fecha", None)
        if area and fecha and hi and hf:
            qs = Reserva.objects.filter(area_comun=area, fecha=fecha)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.filter(hora_inicio__lt=hf, hora_fin__gt=hi).exists():
                raise serializers.ValidationError("Ya existe una reserva en ese horario.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["usuario"] = user

        obj = Reserva.objects.create(**validated_data)
        try:
            obj.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)
        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)
        instance.save()
        return instance


class ReservaEstadoSerializer(serializers.ModelSerializer):
    estado = EstadoChoiceField(choices=[c[0] for c in Reserva.ESTADOS])

    class Meta:
        model = Reserva
        fields = ["id", "estado"]
        read_only_fields = ["id"]