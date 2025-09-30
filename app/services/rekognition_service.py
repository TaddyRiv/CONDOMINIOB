import base64
import boto3
from django.db.models import Q
from django.conf import settings
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from rest_framework.response import Response

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
    Busca tanto por ExternalImageId como por FaceId.
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

    similarity = matches[0]["Similarity"]
    face = matches[0]["Face"]

    external_id = face.get("ExternalImageId")
    face_id = face.get("FaceId")

    # Intentar con ExternalImageId
    if external_id:
        try:
            usuario = Usuario.objects.get(pk=external_id)
            return usuario, similarity
        except Usuario.DoesNotExist:
            pass

    # Intentar con aws_face_id
    if face_id:
        try:
            usuario = Usuario.objects.get(aws_face_id=face_id)
            return usuario, similarity
        except Usuario.DoesNotExist:
            pass

    return None, similarity

def detectar_placa(base64_image: str):
    """
    Usa Rekognition para detectar texto (placa) en la imagen.
    """
    image_bytes = base64.b64decode(base64_image)

    response = rekognition.detect_text(Image={"Bytes": image_bytes})
    textos = response.get("TextDetections", [])

    posibles = []
    for t in textos:
        if t["Type"] == "LINE":  # líneas completas de texto
            posibles.append(t["DetectedText"])

    return posibles


def verificar_placa_en_bd(base64_image: str):
    """
    Detecta la placa en la imagen y verifica si existe en la BD.
    """
    posibles = detectar_placa(base64_image)

    for placa in posibles:
        # Normalizamos (quitar espacios, mayúsculas)
        placa_norm = placa.replace(" ", "").upper()

        try:
            vehiculo = Vehiculo.objects.get(placa__iexact=placa_norm)
            return vehiculo, placa_norm
        except Vehiculo.DoesNotExist:
            continue

    return None, posibles

def rekognition_verificar_placa(request):
    foto_base64 = request.data.get("foto")
    tipo = request.data.get("tipo", "ENTRADA")

    # 👇 Detectar texto con Rekognition
    image_bytes = base64.b64decode(foto_base64)
    response = rekognition.detect_text(Image={"Bytes": image_bytes})

    posibles = [d["DetectedText"].strip().upper()
                for d in response["TextDetections"]
                if d["Type"] == "WORD"]

    print("Posibles detectados:", posibles)

    # 👇 Buscar cualquiera de los detectados en BD
    vehiculo = Vehiculo.objects.filter(
        placa__in=posibles
    ).first()

    if vehiculo:
        return Response({
            "mensaje": "Acceso permitido",
            "vehiculo": {
                "id": vehiculo.id,
                "placa": vehiculo.placa,
                "apartamento": vehiculo.apartamento.numero if vehiculo.apartamento else None
            }
        })
    else:
        return Response({
            "mensaje": "Acceso denegado",
            "posibles_detectados": posibles
        }, status=403)