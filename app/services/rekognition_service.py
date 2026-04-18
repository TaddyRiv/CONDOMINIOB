import base64
import boto3
from django.conf import settings
from app.models.usuario import Usuario

rekognition = boto3.client(
    "rekognition",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME,
)

# 🔹 Usa la colección real de AWS
COLLECTION_ID = "usuarios-condominio"

def registrar_usuario_en_rekognition(usuario: Usuario):
    """
    Envía la foto (base64) de un Usuario a AWS Rekognition y guarda el FaceId.
    """
    if not usuario.foto:
        return None

    # ⚠️ si tu foto viene con "data:image/jpeg;base64,..." cortamos la cabecera
    image_bytes = base64.b64decode(usuario.foto.split(",")[-1])

    response = rekognition.index_faces(
        CollectionId=COLLECTION_ID,
        Image={"Bytes": image_bytes},
        ExternalImageId=str(usuario.id),
        DetectionAttributes=["DEFAULT"],
    )

    if response.get("FaceRecords"):
        face_id = response["FaceRecords"][0]["Face"]["FaceId"]
        usuario.aws_face_id = face_id
        usuario.save(update_fields=["aws_face_id"])
        return face_id
    return None


def verificar_usuario_por_foto(base64_image: str):
    """
    Compara una imagen con la colección y devuelve el usuario si hay coincidencia.
    """
    image_bytes = base64.b64decode(base64_image.split(",")[-1])

    response = rekognition.search_faces_by_image(
        CollectionId=COLLECTION_ID,
        Image={"Bytes": image_bytes},
        MaxFaces=1,
        FaceMatchThreshold=85
    )

    matches = response.get("FaceMatches", [])
    if not matches:
        return None, None

    face = matches[0]["Face"]
    face_id = face["FaceId"]
    similarity = matches[0]["Similarity"]

    try:
        usuario = Usuario.objects.get(aws_face_id=face_id)
        return usuario, similarity
    except Usuario.DoesNotExist:
        return None, similarity
