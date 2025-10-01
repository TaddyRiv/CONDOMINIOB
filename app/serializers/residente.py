from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from app.models.usuario import Usuario
from app.models.apartamento import Apartamento
from app.models.residencia import Residencia
from app.serializers.usuario import Base64ImageField

class ResidenteAltaSerializer(serializers.Serializer):
    # Datos del usuario
    nombre = serializers.CharField(max_length=150)
    ci = serializers.CharField(max_length=20)
    correo = serializers.EmailField()
    telefono = serializers.CharField(max_length=20, allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    foto = Base64ImageField(required=False, allow_null=True)  # 👈 añadido

    apartamento_id = serializers.IntegerField(required=True)

    @transaction.atomic
    def create(self, validated_data):
        apto = validated_data.pop('__apartamento')
        nombre = validated_data.pop('nombre')
        correo = validated_data.pop('correo')
        ci = validated_data.pop('ci')
        telefono = validated_data.pop('telefono', '')
        fecha_nacimiento = validated_data.pop('fecha_nacimiento', None)
        raw_password = validated_data.pop('password', '123')
        foto = validated_data.pop('foto', None)

        user = Usuario(
            email=correo,
            username=correo,
            ci=ci,
            nombre=nombre,
            telefono=telefono or None,
            fecha_nacimiento=fecha_nacimiento,
            rol=Usuario.Roles.RESIDENTE,
            foto=foto  # 👈 guardar
        )
        user.set_password(raw_password)
        user.is_active = True
        user.save()

        residencia = Residencia.objects.create(
            usuario=user,
            apartamento=apto,
            fecha_inicio=timezone.localdate()
        )
        return {"usuario": user, "residencia": residencia}

    def to_representation(self, instance):
        user = instance["usuario"]
        residencia = instance["residencia"]
        return {
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "ci": user.ci,
                "correo": user.email,
                "telefono": user.telefono,
                "rol": user.rol,
                "fecha_nacimiento": user.fecha_nacimiento.isoformat() if user.fecha_nacimiento else None,
                "foto": f"data:image/jpeg;base64,{user.foto}" if user.foto else None,  # 👈 añadir foto
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
    correo = serializers.EmailField(source='email')
    password = serializers.CharField(write_only=True, required=False)
    foto = Base64ImageField(required=False, allow_null=True)  # 👈 añadido

    class Meta:
        model = Usuario
        fields = ('id', 'nombre', 'ci', 'correo', 'telefono', 'password', 'fecha_nacimiento', 'rol', 'foto')
        read_only_fields = ('id', 'rol')

    def create(self, validated_data):
        raw_password = validated_data.pop('password', '123')
        validated_data['username'] = validated_data.get('email')
        validated_data['rol'] = Usuario.Roles.RESIDENTE
        user = Usuario(**validated_data)
        user.set_password(raw_password)
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        # Password (si llega uno nuevo)
        raw_password = validated_data.pop('password', None)
        if raw_password:
            instance.set_password(raw_password)

        # Foto (solo si la mandan)
        if 'foto' in validated_data:
            instance.foto = validated_data.pop('foto')

        # El resto de los campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
     
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "nombre": instance.nombre,
            "ci": instance.ci,
            "correo": instance.email,
            "telefono": instance.telefono,
            "rol": instance.rol,
            "fecha_nacimiento": instance.fecha_nacimiento.isoformat() if instance.fecha_nacimiento else None,
            "foto": f"data:image/jpeg;base64,{instance.foto}" if instance.foto else None
        }
    
    