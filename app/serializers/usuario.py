from rest_framework import serializers
from app.models.usuario import Usuario
import base64

class Base64ImageField(serializers.Field):
    def to_representation(self, value):
        if not value:
            return None
        # Siempre devolver un dataURL válido
        str_value = str(value)
        if str_value.startswith("data:image"):
            return str_value
        return f"data:image/jpeg;base64,{str_value}"

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError("La imagen debe estar en formato base64.")
        if data.startswith("data:image"):
            data = data.split(",", 1)[1]

        try:
            base64.b64decode(data)
        except Exception:
            raise serializers.ValidationError("Cadena base64 inválida.")

        return data

class UsuarioListSerializer(serializers.ModelSerializer):
    foto = Base64ImageField(required=False, allow_null=True)
    residencia_activa = serializers.SerializerMethodField(read_only=True)
    propiedad_activa = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id", "email", "username", "ci", "rol", "nombre",
            "telefono", "foto", "fecha_nacimiento", "is_active",
            "date_joined",
            "residencia_activa",
            "propiedad_activa",
        ]
        read_only_fields = ["id", "date_joined"]

    def get_residencia_activa(self, obj):
        qs = getattr(obj, "residencia_set", None) or getattr(obj, "residencias", None)
        if qs is None:
            return None
        r = qs.filter(fecha_fin__isnull=True).select_related("apartamento").first()
        if not r:
            return None
        return {
            "id": r.id,
            "apartamento": {
                "id": r.apartamento.id,
                "numero": r.apartamento.numero,
                "bloque": getattr(r.apartamento, "bloque", None),
                "estado": getattr(r.apartamento, "estado", None),
            },
            "fecha_inicio": r.fecha_inicio.isoformat() if r.fecha_inicio else None,
        }

    def get_propiedad_activa(self, obj):
        qs = getattr(obj, "propiedad_set", None) or getattr(obj, "propiedades", None)
        if qs is None:
            return None
        p = qs.filter(fecha_fin__isnull=True).select_related("apartamento").first()
        if not p:
            return None
        return {
            "id": p.id,
            "apartamento": {
                "id": p.apartamento.id,
                "numero": p.apartamento.numero,
                "bloque": getattr(p.apartamento, "bloque", None),
                "estado": getattr(p.apartamento, "estado", None),
            },
            "fecha_inicio": p.fecha_inicio.isoformat() if p.fecha_inicio else None,
        }


# --------- CREATE ----------
class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    foto = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Usuario
        fields = [
            "id", "email", "username", "ci", "rol", "nombre",
            "telefono", "foto", "fecha_nacimiento", "password",
        ]
        extra_kwargs = {
            "telefono": {"required": False, "allow_null": True, "allow_blank": True},
            "fecha_nacimiento": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario

    def to_representation(self, instance):
        """Usar el mismo formato de salida que UsuarioListSerializer"""
        return UsuarioListSerializer(instance, context=self.context).data


# --------- UPDATE / PATCH ----------
class UsuarioUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, min_length=6)
    foto = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Usuario
        fields = [
            "email", "username", "ci", "rol", "nombre",
            "telefono", "foto", "fecha_nacimiento", "password", "is_active",
        ]

    def update(self, instance, validated_data):
     pwd = validated_data.pop("password", None)

     if "foto" in validated_data:
        # Si es None => borrar
        if validated_data["foto"] is None:
            instance.foto = None
        else:
            # Aquí el campo es un string base64 → lo guardas directo
            instance.foto = validated_data["foto"]
        validated_data.pop("foto")

     for k, v in validated_data.items():
        setattr(instance, k, v)

     if pwd:
        instance.set_password(pwd)
     instance.save()
     return instance

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"