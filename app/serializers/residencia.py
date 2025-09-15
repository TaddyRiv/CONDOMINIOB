from rest_framework import serializers
from app.models.usuario import Usuario
from app.models.apartamento import Apartamento
from app.models.residencia import Residencia
from django.utils import timezone
from django.db import transaction

class ResidenciaSerializer(serializers.ModelSerializer):
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), source='usuario', write_only=True
    )
    apartamento_id = serializers.PrimaryKeyRelatedField(
        queryset=Apartamento.objects.all(), source='apartamento', write_only=True
    )

    # representación de solo lectura
    usuario = serializers.SerializerMethodField(read_only=True)
    apartamento = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Residencia
        fields = ('id', 'usuario_id', 'apartamento_id', 'fecha_inicio', 'fecha_fin',
                  'usuario', 'apartamento', 'created_at')
        read_only_fields = ('id', 'created_at', 'usuario', 'apartamento')

    def get_usuario(self, obj):
        return {
            "id": obj.usuario.id,
            "email": getattr(obj.usuario, 'email', None),
            "nombre": getattr(obj.usuario, 'first_name', None),
            "apellido": getattr(obj.usuario, 'last_name', None),
            "rol": getattr(obj.usuario, 'rol', None),
        }

    def get_apartamento(self, obj):
        return {"id": obj.apartamento.id, "numero": obj.apartamento.numero}

    def validate(self, data):
        usuario = data.get('usuario') or getattr(self.instance, 'usuario', None)
        fecha_inicio = data.get('fecha_inicio') or getattr(self.instance, 'fecha_inicio', None)
        fecha_fin = data.get('fecha_fin') if 'fecha_fin' in data else getattr(self.instance, 'fecha_fin', None)

        if fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError("La fecha_fin no puede ser anterior a la fecha_inicio.")

        # Validar que no existan DOS residencias activas para el mismo usuario
        if fecha_fin is None and usuario:
            existe_activa = Residencia.objects.filter(usuario=usuario, fecha_fin__isnull=True)
            if self.instance:
                existe_activa = existe_activa.exclude(pk=self.instance.pk)
            if existe_activa.exists():
                raise serializers.ValidationError("El usuario ya tiene una residencia activa.")
        return data
            
class ResidenciaAsignarSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    apartamento_id = serializers.IntegerField()
    fecha_inicio = serializers.DateField(required=False)  # default: hoy

    def validate(self, attrs):
        # Usuario existente
        try:
            usuario = Usuario.objects.get(pk=attrs['usuario_id'])
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"usuario_id": "El usuario no existe."})

        # Apartamento existente
        try:
            apartamento = Apartamento.objects.get(pk=attrs['apartamento_id'])
        except Apartamento.DoesNotExist:
            raise serializers.ValidationError({"apartamento_id": "El apartamento no existe."})

        # Regla: solo una residencia ACTIVA por usuario
        if Residencia.objects.filter(usuario=usuario, fecha_fin__isnull=True).exists():
            raise serializers.ValidationError("El usuario ya tiene una residencia activa.")

        attrs['__usuario'] = usuario
        attrs['__apartamento'] = apartamento
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        usuario = validated_data.pop('__usuario')
        apartamento = validated_data.pop('__apartamento')

        # Lock de apartamento por seguridad (evita carreras si luego decides validar capacidad/estado)
        apartamento = Apartamento.objects.select_for_update().get(pk=apartamento.pk)

        fecha_inicio = validated_data.pop('fecha_inicio', None) or timezone.localdate()

        residencia = Residencia.objects.create(
            usuario=usuario,
            apartamento=apartamento,
            fecha_inicio=fecha_inicio
        )

        # (Opcional) Cambiar estado del apartamento aquí si quisieras:
        # apartamento.estado = "OCUPADO"
        # apartamento.save(update_fields=["estado"])

        return residencia

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "usuario": {
                "id": instance.usuario.id,
                "nombre": getattr(instance.usuario, 'nombre', None),
                "ci": instance.usuario.ci,
                "email": instance.usuario.email,
                "telefono": instance.usuario.telefono,
                "rol": getattr(instance.usuario, 'rol', None),
                "fecha_nacimiento": instance.usuario.fecha_nacimiento.isoformat() if instance.usuario.fecha_nacimiento else None
            },
            "apartamento": {
                "id": instance.apartamento.id,
                "numero": instance.apartamento.numero,
                "bloque": instance.apartamento.bloque,
                "estado": instance.apartamento.estado,
            },
            "fecha_inicio": instance.fecha_inicio.isoformat(),
            "fecha_fin": instance.fecha_fin.isoformat() if instance.fecha_fin else None
        }
