from rest_framework import serializers
from app.models.usuario import Usuario
from app.models.propiedad import Propiedad
from app.models.apartamento import Apartamento
from app.models.residencia import Residencia
from django.utils import timezone
from django.db import transaction


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
        
class PropiedadAsignarSerializer(serializers.Serializer):
    
    
    usuario_id = serializers.IntegerField()
    apartamento_id = serializers.IntegerField()
    fecha_inicio = serializers.DateField(required=False)   # default: hoy
    fecha_fin = serializers.DateField(required=False, allow_null=True)
    vive = serializers.BooleanField(required=False, default=False)   # si vive, crear Residencia

    def validate(self, attrs):
        # Usuario
        try:
            usuario = Usuario.objects.get(pk=attrs['usuario_id'])
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"usuario_id": "El usuario no existe."})

        # Apartamento
        try:
            apartamento = Apartamento.objects.get(pk=attrs['apartamento_id'])
        except Apartamento.DoesNotExist:
            raise serializers.ValidationError({"apartamento_id": "El apartamento no existe."})

        fi = attrs.get('fecha_inicio')
        ff = attrs.get('fecha_fin')

        # Reglas básicas de fechas
        if ff and fi and ff < fi:
            raise serializers.ValidationError({"fecha_fin": "No puede ser anterior a fecha_inicio."})

        # Evitar dos propietarios activos en mismo apartamento
        if not ff:
            activo_otro = Propiedad.objects.filter(apartamento=apartamento, fecha_fin__isnull=True).exists()
            if activo_otro:
                raise serializers.ValidationError({"apartamento_id": "El apartamento ya tiene un propietario activo."})

        # Evitar solapamiento de rangos (simple) con otras propiedades del mismo apartamento
        # [fi, ff] solapa con cualquiera que cumpla:
        # (ff_nueva is null o ff_nueva >= fi_existente) y (ff_existente is null o ff_existente >= fi_nueva)
        fi_nueva = fi or timezone.localdate()
        qs = Propiedad.objects.filter(apartamento=apartamento)
        for p in qs:
            fi_old = p.fecha_inicio
            ff_old = p.fecha_fin
            # si no hay fin, tómalo como abierto
            ff_cmp = ff or timezone.localdate().replace(year=9999)  # "infinito" simple
            ff_old_cmp = ff_old or timezone.localdate().replace(year=9999)
            if (fi_nueva <= ff_old_cmp) and (fi_old <= ff_cmp):
                raise serializers.ValidationError({"apartamento_id": "Rango de propiedad se solapa con otra existente."})

        attrs['__usuario'] = usuario
        attrs['__apartamento'] = apartamento
        attrs['__fi'] = fi_nueva
        attrs['__ff'] = ff
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        usuario = validated_data.pop('__usuario')
        apartamento = validated_data.pop('__apartamento')
        fi = validated_data.pop('__fi')
        ff = validated_data.pop('__ff')
        vive = validated_data.get('vive', False)

        # Lock apartamento por seguridad
        apartamento = Apartamento.objects.select_for_update().get(pk=apartamento.pk)

        # Crear Propiedad
        propiedad = Propiedad.objects.create(
            usuario=usuario,
            apartamento=apartamento,
            fecha_inicio=fi,
            fecha_fin=ff
        )

        # Si VIVE, crear Residencia (si no tiene activa)
        residencia = None
        if vive:
            if Residencia.objects.filter(usuario=usuario, fecha_fin__isnull=True).exists():
                raise serializers.ValidationError("El usuario ya tiene una residencia activa.")
            residencia = Residencia.objects.create(
                usuario=usuario,
                apartamento=apartamento,
                fecha_inicio=fi
            )
            # Si quieres, aquí puedes cambiar estado del apartamento a OCUPADO
            # apartamento.estado = "OCUPADO"
            # apartamento.save(update_fields=['estado'])

        return {"propiedad": propiedad, "residencia": residencia}

    def to_representation(self, instance):
        propiedad = instance["propiedad"]
        residencia = instance["residencia"]
        data = {
            "propiedad": {
                "id": propiedad.id,
                "usuario": {
                    "id": propiedad.usuario.id,
                    "nombre": getattr(propiedad.usuario, 'nombre', None),
                    "email": propiedad.usuario.email,
                    "rol": getattr(propiedad.usuario, 'rol', None),
                },
                "apartamento": {
                    "id": propiedad.apartamento.id,
                    "numero": propiedad.apartamento.numero,
                    "bloque": propiedad.apartamento.bloque,
                    "estado": propiedad.apartamento.estado,
                },
                "fecha_inicio": propiedad.fecha_inicio.isoformat(),
                "fecha_fin": propiedad.fecha_fin.isoformat() if propiedad.fecha_fin else None
            }
        }
        if residencia:
            data["residencia"] = {
                "id": residencia.id,
                "fecha_inicio": residencia.fecha_inicio.isoformat(),
                "fecha_fin": residencia.fecha_fin.isoformat() if residencia.fecha_fin else None
            }
        return data
    
class UsuarioPropietarioCreateSerializer(serializers.ModelSerializer):
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
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        validated_data['rol'] = getattr(Usuario.Roles, 'DUEÑO', 'DUEÑO')  # o "PROPIETARIO" si así lo nombras

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