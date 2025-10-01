# app/serializers/cargo.py
from rest_framework import serializers
from app.models.cargo import Cargo
from app.models.cargo_servicio import CargoServicio
from app.models.servicio import Servicio
import calendar, datetime

class CargoServicioItemSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source="servicio.nombre", read_only=True)

    class Meta:
        model = CargoServicio
        fields = ["id", "servicio", "servicio_nombre", "cantidad", "precio_unitario", "subtotal"]
        read_only_fields = ["subtotal"]

    def validate(self, attrs):
        """
        Si no envías precio_unitario, usamos el precio actual del Servicio.
        """
        servicio = attrs.get("servicio")  # instancia de Servicio
        precio_unitario = attrs.get("precio_unitario")
        if precio_unitario is None and servicio:
            attrs["precio_unitario"] = servicio.precio
        return attrs


class CargoSerializer(serializers.ModelSerializer):
    detalles = CargoServicioItemSerializer(many=True, required=False)
    apartamento_numero = serializers.CharField(source="apartamento.numero", read_only=True)

    # CAMBIOS CLAVES:
    # 1) fecha_vencimiento calculada (no existe en el modelo)
    fecha_vencimiento = serializers.SerializerMethodField()
    # 2) 'notas' mapea al campo 'descripcion' del modelo
    notas = serializers.CharField(source="descripcion", allow_blank=True, required=False)

    class Meta:
        model = Cargo
        fields = [
            "id",
            "apartamento",
            "apartamento_numero",
            "periodo",
            "fecha_vencimiento",
            "estado",
            "total",
            "pagado",
            "notas",
            "detalles",
        ]
        read_only_fields = ["estado", "total", "pagado"]

    def get_fecha_vencimiento(self, obj: Cargo):
        y, m = obj.periodo.year, obj.periodo.month
        last_day = calendar.monthrange(y, m)[1]
        return datetime.date(y, m, last_day)

    def _first_day_of_month(self, d: datetime.date) -> datetime.date:
        return datetime.date(d.year, d.month, 1)

    def validate(self, attrs):
        """
        Normaliza 'periodo' al primer día del mes para que respete el unique_together (apartamento, periodo).
        """
        periodo = attrs.get("periodo") or getattr(self.instance, "periodo", None)
        if periodo:
            attrs["periodo"] = self._first_day_of_month(periodo)
        return attrs

    def create(self, validated_data):
        detalles_data = validated_data.pop("detalles", [])
        cargo = Cargo.objects.create(**validated_data)

        for item in detalles_data:
            # item ya pasó por validate() del nested serializer (precio_unitario listo)
            CargoServicio.objects.create(cargo=cargo, **item)

        cargo.recomputar_total()
        return cargo

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop("detalles", None)

        # Actualiza campos simples (incluye 'descripcion' mapeado desde 'notas')
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # Si mandan 'detalles', hacemos estrategia simple: borrar y recrear
        if detalles_data is not None:
            instance.detalles.all().delete()
            for item in detalles_data:
                CargoServicio.objects.create(cargo=instance, **item)
            instance.recomputar_total()

        return instance
