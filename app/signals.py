from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group
from app.models.usuario import Usuario
from app.services.rekognition_service import registrar_usuario_en_rekognition
from django.db.models.signals import post_save


@receiver(post_migrate)
def crear_grupos_basicos(sender, **kwargs):
    # Evita ejecutarse en apps ajenas
    if sender.name != "app":
        return
    for nombre in ["admin", "empleado", "residente"]:
        Group.objects.get_or_create(name=nombre)

@receiver(post_save, sender=Usuario)
def registrar_rostro_automatico(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un usuario con foto, se registra en AWS Rekognition.
    """
    if instance.foto and not instance.aws_face_id:
        try:
            face_id = registrar_usuario_en_rekognition(instance)
            if face_id:
                instance.aws_face_id = face_id
                instance.save(update_fields=["aws_face_id"])
                print(f"✅ Usuario {instance.email} registrado en Rekognition con face_id {face_id}")
        except Exception as e:
            print(f"⚠️ Error registrando rostro automáticamente para {instance.email}: {e}")
