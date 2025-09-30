from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.serializers.rekognition import VerificarAccesoSerializer
from app.services.rekognition_service import verificar_usuario_por_foto
from app.services.rekognition_service import registrar_usuario_en_rekognition
from app.models.usuario import Usuario
from app.models.acceso import Camara, Reconocimiento, IntentoAcceso, EntradaSalida
from app.services.rekognition_service import verificar_placa_en_bd
from app.views import usuario

class VerificarAccesoView(APIView):
    """
    Endpoint que recibe una foto en base64 y devuelve si el usuario puede acceder.
    """

    def post(self, request):
        serializer = VerificarAccesoSerializer(data=request.data)
        if serializer.is_valid():
            foto = serializer.validated_data["foto"]
            camara_id = serializer.validated_data["camara_id"]
            tipo = serializer.validated_data["tipo"]

            try:
                camara = Camara.objects.get(pk=camara_id)
            except Camara.DoesNotExist:
                return Response({"error": "Cámara no encontrada"}, status=status.HTTP_404_NOT_FOUND)

            # 1️⃣ Reconocimiento en AWS Rekognition
            usuario, similarity = verificar_usuario_por_foto(foto)

            # 2️⃣ Guardar Reconocimiento
            reconocimiento = Reconocimiento.objects.create(
                tipo="ROSTRO",
                camara=camara,
                confianza=similarity or 0
            )

            # 3️⃣ Guardar IntentoAcceso
            intento = IntentoAcceso.objects.create(
    reconocimiento=reconocimiento,
    usuario=usuario if usuario else None,
    punto_acceso=camara.punto_acceso,
    resultado="ACEPTADO" if usuario else "DENEGADO",
    motivo=None if usuario else "No reconocido"
)

            # 4️⃣ Guardar Entrada/Salida
            if intento.usuario:
                 EntradaSalida.objects.create(
        intento=intento,
        tipo=tipo
)

            # 5️⃣ Respuesta al cliente
            if usuario:
                return Response({
                    "mensaje": "Acceso permitido",
                    "usuario": {
                        "id": usuario.id,
                        "nombre": usuario.nombre,
                        "email": usuario.email,
                    },
                    "similaridad": similarity,
                    "camara": camara.nombre,
                    "tipo": tipo
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "mensaje": "Acceso denegado",
                    "similaridad": similarity or 0,
                    "camara": camara.nombre,
                    "tipo": tipo
                }, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrarRostroUsuario(APIView):
    """
    Endpoint para registrar la foto de un usuario en AWS Rekognition.
    """

    def post(self, request, usuario_id):
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        face_id = registrar_usuario_en_rekognition(usuario)

        if face_id:
            usuario.aws_face_id = face_id
            usuario.save(update_fields=["aws_face_id"])
            return Response({
                "mensaje": "Usuario registrado en Rekognition",
                "usuario_id": usuario.id,
                "face_id": face_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No se pudo registrar el rostro"}, status=status.HTTP_400_BAD_REQUEST)
        

class SincronizarUsuariosView(APIView):
    """
    Sincroniza todos los usuarios con foto hacia AWS Rekognition.
    Solo mandará los que aún no tengan aws_face_id.
    """

    def post(self, request):
        procesados = []
        errores = []

        usuarios = Usuario.objects.filter(foto__isnull=False).exclude(foto="").filter(aws_face_id__isnull=True)

        for usuario in usuarios:
            try:
                face_id = registrar_usuario_en_rekognition(usuario)
                if face_id:
                    usuario.aws_face_id = face_id
                    usuario.save(update_fields=["aws_face_id"])
                    procesados.append({
                        "id": usuario.id,
                        "email": usuario.email,
                        "face_id": face_id
                    })
            except Exception as e:
                errores.append({
                    "id": usuario.id,
                    "email": usuario.email,
                    "error": str(e)
                })

        return Response({
            "total": usuarios.count(),
            "procesados": procesados,
            "errores": errores
        }, status=status.HTTP_200_OK)
    
class ListarCamarasView(APIView):
    def get(self, request):
        camaras = Camara.objects.filter(activa=True)
        data = [
            {"id": c.id, "nombre": c.nombre, "ubicacion": c.ubicacion, "punto_acceso": c.punto_acceso.nombre}
            for c in camaras
        ]
        return Response(data)
    
class VerificarPlacaView(APIView):
    """
    Endpoint para verificar acceso de un vehículo mediante foto de su placa.
    """

    def post(self, request):
        foto = request.data.get("foto")
        if not foto:
            return Response({"error": "Se requiere foto en base64"}, status=status.HTTP_400_BAD_REQUEST)

        vehiculo, posibles = verificar_placa_en_bd(foto)

        if vehiculo:
            return Response({
                "mensaje": "Acceso permitido",
                "vehiculo": {
                    "id": vehiculo.id,
                    "placa": vehiculo.placa,
                    "apartamento": vehiculo.apartamento.numero if vehiculo.apartamento else None,
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "mensaje": "Acceso denegado",
            "posibles_detectados": posibles
        }, status=status.HTTP_403_FORBIDDEN)