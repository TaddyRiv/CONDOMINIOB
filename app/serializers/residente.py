from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from app.models.usuario import Usuario
from app.models.apartamento import Apartamento
from app.models.residencia import Residencia

class ResidenteAltaSerializer(serializers.Serializer):
    # Datos del usuario
    nombre = serializers.CharField(max_length=150)
    ci = serializers.CharField(max_length=20)
    correo = serializers.EmailField()
    telefono = serializers.CharField(max_length=20, allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, required=False)  # por defecto "123"
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)

    # Apartamento: obligatorio y elegido manualmente
    apartamento_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        # Unicidad de email y CI
        if Usuario.objects.filter(email=attrs['correo']).exists():
            raise serializers.ValidationError({"correo": "Ya existe un usuario con este correo."})
        if Usuario.objects.filter(ci=attrs['ci']).exists():
            raise serializers.ValidationError({"ci": "Ya existe un usuario con este CI."})

        # Verificar apartamento existe (ya NO exigimos estado == DISPONIBLE)
        try:
            apto = Apartamento.objects.get(pk=attrs['apartamento_id'])
        except Apartamento.DoesNotExist:
            raise serializers.ValidationError({"apartamento_id": "El apartamento no existe."})
        
        attrs['__apartamento'] = apto
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Lock del apartamento para evitar condiciones de carrera
        apto = validated_data.pop('__apartamento')
        apto = Apartamento.objects.select_for_update().get(pk=apto.pk)

        nombre = validated_data.pop('nombre')
        correo = validated_data.pop('correo')
        ci = validated_data.pop('ci')
        telefono = validated_data.pop('telefono', '')
        fecha_nacimiento = validated_data.pop('fecha_nacimiento', None)
        raw_password = validated_data.pop('password', '123')  # default si no envían

        # Crear Usuario con rol RESIDENTE
        user = Usuario(
            email=correo,
            username=correo,  # cumple REQUIRED_FIELDS del AbstractUser
            ci=ci,
            nombre=nombre,
            telefono=telefono or None,
            fecha_nacimiento=fecha_nacimiento,
            rol=getattr(Usuario.Roles, 'RESIDENTE', 'RESIDENTE')
        )
        user.set_password(raw_password)
        user.is_active = True
        user.save()

        # Regla extra de seguridad: una residencia activa por usuario
        if Residencia.objects.filter(usuario=user, fecha_fin__isnull=True).exists():
            raise serializers.ValidationError("El usuario ya tiene una residencia activa.")

        # Crear Residencia (fecha_inicio = hoy)
        residencia = Residencia.objects.create(
            usuario=user,
            apartamento=apto,
            fecha_inicio=timezone.localdate()
        )

        # Nota: no modificamos el estado del apartamento aquí (queda como esté).
        return {"usuario": user, "residencia": residencia}

    def to_representation(self, instance):
        user = instance["usuario"]
        residencia = instance["residencia"]
        return {
            "usuario": {
                "id": user.id,
                "nombre": getattr(user, 'nombre', None),
                "ci": user.ci,
                "email": user.email,
                "telefono": user.telefono,
                "rol": getattr(user, 'rol', None),
                "fecha_nacimiento": user.fecha_nacimiento.isoformat() if user.fecha_nacimiento else None
            },
            "residencia": {
                "id": residencia.id,
                "apartamento": {
                    "id": residencia.apartamento.id,
                    "numero": residencia.apartamento.numero,
                    "bloque": residencia.apartamento.bloque,
                    "estado": residencia.apartamento.estado,
                },
                "fecha_inicio": residencia.fecha_inicio.isoformat(),
                "fecha_fin": residencia.fecha_fin.isoformat() if residencia.fecha_fin else None
            }
        }
        
class UsuarioResidenteCreateSerializer(serializers.ModelSerializer):
    # Renombramos "email" a "correo" para el payload
    correo = serializers.EmailField(source='email')
    password = serializers.CharField(write_only=True, required=False)  # default "123"

    class Meta:
        model = Usuario
        fields = ('id', 'nombre', 'ci', 'correo', 'telefono', 'password', 'fecha_nacimiento', 'rol')
        read_only_fields = ('id', 'rol')

    def validate(self, attrs):
        email = attrs['email']
        ci = attrs['ci']
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError({"correo": "Ya existe un usuario con este correo."})
        if Usuario.objects.filter(ci=ci).exists():
            raise serializers.ValidationError({"ci": "Ya existe un usuario con este CI."})
        return attrs

    def create(self, validated_data):
        raw_password = validated_data.pop('password', '123')
        # Aseguramos username para AbstractUser
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        # Rol residente
        validated_data['rol'] = getattr(Usuario.Roles, 'RESIDENTE', 'RESIDENTE')

        user = Usuario(**validated_data)
        user.set_password(raw_password)
        user.is_active = True
        user.save()
        return user

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "nombre": instance.nombre,
            "ci": instance.ci,
            "correo": instance.email,
            "telefono": instance.telefono,
            "rol": instance.rol,
            "fecha_nacimiento": instance.fecha_nacimiento.isoformat() if instance.fecha_nacimiento else None
        }