from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group
from app.models.usuario import Usuario
from app.services.rekognition_service import registrar_usuario_en_rekognition
@receiver(post_migrate)
def crear_grupos_basicos(sender, **kwargs):
    # Evita ejecutarse en apps ajenas
    if sender.name != "app":
        return
    for nombre in ["admin", "empleado", "residente"]:
        Group.objects.get_or_create(name=nombre)

def registrar_usuario_en_aws(sender, instance, created, **kwargs):
    """
    Cada vez que se cree un Usuario con foto,
    se enviará automáticamente a AWS Rekognition.
    """
    if created and instance.foto:
        try:
            face_id = registrar_usuario_en_rekognition(instance)
            print(f"[AWS] Usuario {instance.id} registrado en Rekognition con FaceId: {face_id}")
        except Exception as e:
            print(f"[AWS ERROR] No se pudo registrar usuario {instance.id}: {e}")